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
from queue import Queue
        
#my libs
import RESTEndpoints
from ServerContext import ElementTypes
from Job import JobRunner, BaseJob
from JobManager import JobManager
import intercom
import NodeInterface


logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("flask").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)
class Node(BaseNode):
    
    def __init__(self):
        BaseNode.__init__(self)
        self.num_cores = multiprocessing.cpu_count()
        
        self.jobManager = JobManager()
        
        self.result_queue = Queue(0)
        self.job_queue = Queue(0)
        
        self.interfaces_lock = threading.Lock()
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
        #job thread (new incoming jobs or finished jobs)
        self.job_thread = threading.Thread(target=self.job_processor)
        self.job_thread.start()
            
    #START HERE
    ####
    ###
    ##
    #
    def job_processor(self):
        self.logger.debug('in the job processor thread')
        while (True):
            sc = self.get_server_context()
            job_element = sc.job_queue.get()
            #the job submitted by the user
            job = BaseJob()
            job.job_from_dictionary(job_element)
            
            if (job.finished==True):
                #add as a result
                self.result_queue.put(job)
                continue
            else:
                #add as a job
                self.job_queue.put(job)
            
        
    def general_processor(self):
        self.logger.debug('in the processor thread')
        while(True):
            sc = self.get_server_context()
            general_element = self.request_general_elements().get()
            
            if (general_element['type']==ElementTypes.slave_node_recv):
                self.logger.debug('adding a JobInterface to the node')
                
                node_data = general_element['json_data']
                node_interface = NodeInterface.NodeInterface()
                
                #update the nodes counts. This means that the node
                #is up to date.
                node_interface.NodeInterface_from_dictionary(node_data) #only need ip and port
                node_interface.update_variables()
                
                #update the interfaces list
                self.interfaces_lock.acquire()
                self.interfaces.append(node_interface)
                self.interfaces_lock.release()
                
                self.logger.debug('(IFL) interfaces: %s' % self.interfaces)
                
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
        
        
        
        