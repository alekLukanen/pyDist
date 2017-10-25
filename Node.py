#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 19:54:09 2017

@author: lukanen
"""

#standard libs
import json
import time

class BaseNode(object):
    
    def __init__(self):
        self.name = 'default_name'
        self.id = 'default_id'
        self.ip = "0.0.0.0"
        self.port = 9000
        self.num_cores = 0
        self.num_active_jobs = 0
        #added to a new node's id. 
        #makes sure that all nodes have a unique id.
        self.id_tick = 0 
        self.job_id_tick = 0
        
    def increment_id_tick(self):
        self.id_tick+=1
        
    def increment_job_id_tick(self):
        self.job_id_tick+=1
        
    def get_address(self):
        return "http://%s:%d" % (self.ip, self.port)
        
    def convert_to_dictionary(self):
        node_as_dictionary = {'name': self.name,
                              'id': self.id,
                              'ip': self.ip,
                              'port': self.port,
                              'num_cores': self.num_cores,
                              'num_active_jobs': self.num_active_jobs,
                              'id_tick': self.id_tick}
        return node_as_dictionary
        
    def convert_to_json(self):
        return json.dumps(self.convert_to_dictionary())
    
    def BaseNode_from_dictionary(self, data):
        if (data!=None):
            self.name = data["name"]
            self.id = data["id"]
            self.ip = data["ip"]
            self.port = data["port"]
            self.num_cores = data["num_cores"]
            self.num_active_jobs = data["num_active_jobs"]
        


import logging
import sys
import threading
import multiprocessing
        
#my libs
import RESTEndpoints
from ServerContext import ElementTypes
from Job import JobRunner, BaseJob, JobServer
from JobManager import JobManager
import intercom


logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("flask").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)
class Node(BaseNode):
    
    def __init__(self):
        BaseNode.__init__(self)
        self.num_cores = multiprocessing.cpu_count()
        
        self.jobManager = JobManager()
        self.interfaces = []
        
        #create and run the RESTEnpoints module in another thread
        self.REST_thread = None
        self.general_thread = None
        self.message_thread = None
        self.job_thread = None
        
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)s - %(funcName)20s() ] - %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
        self.logger = logging.getLogger()
        
    def boot(self, ip, port):
        self.logger.debug("starting the node (server and client)")
        self.ip = ip
        self.port = port
        self.create_server()
        time.sleep(1)
        
    def connect(self, server_ip, server_port):
        self.logger.debug("connecting to %s:%d" % (server_ip,server_port))
        response = intercom.connect_as_slave(server_ip, server_port, self)
        if (response==None):
            print ("could not connect to that host, trying again")
        else:
            print ("connected to the host")
        
    def create_server(self):
        #rest server thread
        self.REST_thread = threading.Thread(target=RESTEndpoints.boot,args=(self.ip,self.port,self,))
        self.REST_thread.start()
        #general info thread
        self.general_thread = threading.Thread(target=self.general_processor)
        self.general_thread.start()
        #message thread
        self.message_thread = threading.Thread(target=self.message_processor)
        self.message_thread.start()
        #job thread (new incoming jobs)
        self.job_thread = threading.Thread(target=self.job_processor)
        self.job_thread.start()
        
        self.result_thread = threading.Thread(target=self.result_processor)
        self.result_thread.start()

    def result_processor(self):
        self.logger.debug('in the result processor thread')
        while (True):
            result = self.get_server_context().processor.get_result() #a new result for the master node
            job_for_server = JobServer()
            job_for_server.job_from_dictionary(result.convert_to_dictionary())
            job_for_server.finished = True
            intercom.post_job(job_for_server.root_node.ip
                              , job_for_server.root_node.port, job_for_server)
            

    #START HERE
    ####
    ###
    ##
    #
    def job_processor(self):
        self.logger.debug('in the job processor thread')
        while (True):
            sc = self.get_server_context()
            job_element = self.request_job_elements().get()
            #the job submitted by the user
            job = JobServer()
            job.job_from_dictionary(job_element)
            
            is_finished = sc.process_job(job)
            if (is_finished):
                sent = sc.send_job_to_a_client(job) #T/F
                if (sent):
                    sc.processed_jobs[self.job_id_tick] = job
                    self.increment_job_id_tick()
                else:
                    sc.add_pending_job(job)
        
    def message_processor(self):
        self.logger.debug('in the message processor thread')
        while (True):
            sc = self.get_server_context()
            message_element = self.request_message_elements().get()
            #do something with message here
            #
            #
            
            sc.acquire_past_messages().append(message_element)
            self.logger.debug("message added: %s" % message_element)
            
        
    def general_processor(self):
        self.logger.debug('in the processor thread')
        while(True):
            sc = self.get_server_context()
            general_element = self.request_general_elements().get()
            
            if (general_element['type']==ElementTypes.slave_node_recv):
                self.logger.debug('adding a slave node to the node')
                
                slave_node_data = general_element['json_data']
                slave_node = Node()
                slave_node.BaseNode_from_dictionary(slave_node_data)
                sc.add_slave_node(self.id_tick, slave_node)
                
                #connect back to the client to tell them that they have been
                #added as a client. This also servers as info pass to the client
                #so they know where the master node is in the future.
                intercom.connect_as_master(slave_node.ip, slave_node.port, self)
                self.increment_id_tick()
                
            elif (general_element['type']==ElementTypes.master_node_recv):
                self.logger.debug('adding a master node to the node')
                
                master_node_data = general_element['json_data']
                node_id = self.id_tick
                master_node = Node()
                master_node.BaseNode_from_dictionary(master_node_data)
                sc.acquire_masters()[node_id] = master_node
                self.increment_id_tick()
                
            else:
                self.logger.debug('ElementTypes does not contain: %s' % general_element)
                
    
   
    def close_node(self):
        self.logger.debug('closing the node')
        self.request_close_server()
        self.REST_thread.join()
        
    def request_close_server(self):
        self.logger.debug('closing the server')
        intercom.close_server(self.ip, self.port) #close this node's server
        
    def get_server_context(self):
        return RESTEndpoints.sc
        
    def request_slave_nodes(self):
        return self.get_server_context().slave_node_queue
    
    def request_master_nodes(self):
        return self.get_server_context().master_node_queue
    
    def request_general_elements(self):
        return self.get_server_context().general_queue
    
    def request_message_elements(self):
        return self.get_server_context().message_queue
    
    def request_job_elements(self):
        return self.get_server_context().job_queue
        
    #requires a node object
    def add_slave_node(self, node):
        self.logger.debug("adding slave node with name")
        self.slaves[node.id] = node
        
    #requires a node object
    def add_master_node(self, node):
        self.logger.debug("adding master node with name")
        self.masters[node.id] = node
                  
    def log_nodes(self):
        self.logger.debug("self.masters: " + str(self.masters))
        self.logger.debug("self.slaves: " + str(self.slaves))
        
        
        
        