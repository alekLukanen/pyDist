#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 19:54:09 2017

@author: lukanen
"""

#standard libs
import json
import time

#class BaseNode(object):
#    
#    def __init__(self):
#        self.name = 'default_name'
#        self.id = 'default_id'
#        self.ip = "0.0.0.0"
#        self.port = 9000
#        self.server_ip = None
#        self.server_port = None
#        self.num_cores = 0
#        self.num_active_jobs = 0
#        #added to a new node's id. 
#        #makes sure that all nodes have a unique id.
#        self.id_tick = 0 
#        self.job_id_tick = 0
#        
#    def increment_id_tick(self):
#        self.id_tick+=1
#        
#    def increment_job_id_tick(self):
#        self.job_id_tick+=1
#        
#    def get_address(self):
#        return "http://%s:%d" % (self.ip, self.port)
#        
#    def convert_to_dictionary(self):
#        node_as_dictionary = {'name': self.name,
#                              'id': self.id,
#                              'ip': self.ip,
#                              'port': self.port,
#                              'num_cores': self.num_cores,
#                              'num_active_jobs': self.num_active_jobs,
#                              'id_tick': self.id_tick}
#        return node_as_dictionary
#        
#    def convert_to_json(self):
#        return json.dumps(self.convert_to_dictionary())
#    
#    def BaseNode_from_dictionary(self, data):
#        if (data!=None):
#            self.name = data["name"]
#            self.id = data["id"]
#            self.ip = data["ip"]
#            self.port = data["port"]
#            self.num_cores = data["num_cores"]
#            self.num_active_jobs = data["num_active_jobs"]
        


import logging
import sys
import threading
import multiprocessing
from queue import Queue
        
#my libs
import RESTEndpoints as _RESTEndpoints
from ServerContext import ElementTypes
import Job
from JobManager import JobManager
import intercom
import Interfaces


logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("flask").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
class Node(Interfaces.NodeInterface):
    
    def __init__(self):
        Interfaces.NodeInterface.__init__(self)
        
        self.num_cores = multiprocessing.cpu_count()
        
        self.jobManager = JobManager()
        
        self.result_queue = Queue(0)
        self.job_queue = Queue(0)
        
        self.result_added = threading.Event()
        self.result_added.clear()
        
        self.interfaces_lock = threading.Lock()
        self.interfaces = []
        
        #create and run the RESTEnpoints module in another thread
        self.REST_thread = None
        self.general_thread = None
        self.message_thread = None
        self.job_thread = None
        self.job_runner_thread = None
        self.job_manager_thread = None
        
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
    
    #start the rest endpoints and the processor threads.    
    def create_server(self):
        #rest server thread
        self.REST_thread = threading.Thread(target=_RESTEndpoints.boot,args=(self.ip,self.port,self,))
        self.REST_thread.daemon = False
        self.REST_thread.start()
        #general info thread
        self.general_thread = threading.Thread(target=self.general_processor)
        self.general_thread.daemon = True
        self.general_thread.start()
        #job thread (new incoming jobs or finished jobs)
        self.job_thread = threading.Thread(target=self.job_processor)
        self.job_thread.daemon = True
        self.job_thread.start()
        #create runner thread
        self.job_runner_thread = threading.Thread(target=self.job_runner)
        self.job_runner_thread.daemon = True
        self.job_runner_thread.start()
        #job manager thread
        self.job_manager_thread = threading.Thread(target=self.job_manager_processor)
        self.job_manager_thread.daemon = True
        self.job_manager_thread.start()
        
    def update_NodeInt_counts(self):
        self.interfaces_lock.acquire()
        for NodeInt in self.interfaces:
            NodeInt.update_counts()
        self.interfaces_lock.release()
    
    #with the jobs in the job_queue send the jobs to the various
    #job managers/Node interfaces.        
    def job_runner(self):
        self.logger.debug('in the job runner thread')
        previous_job = None
        num_jobs_dequed = 0
        while(True):
            if (previous_job==None):
                #self.logger.debug('(QUEUE %d) getting job from queue' % num_jobs_dequed)
                job = self.job_queue.get()
                num_jobs_dequed+=1
            else:
                job = previous_job
            
            job_placed = False
            if (len(self.jobManager.running_job_dictionary)+self.jobManager.job_q_count<self.jobManager.num_processors):
                #(1) look for a spot on this node
                self.jobManager.add_job(Job.convertBaseToRunner(job))
                self.logger.debug('(JOB>>>HEAD) adding job to this node')
                job_placed = True
            else:
                #(2) look for a spot on other nodes
                self.update_NodeInt_counts() #update the counts first
                job
                self.interfaces_lock.acquire()
                for NodeInt in self.interfaces:
                    if ((NodeInt.num_running+NodeInt.num_queued)<NodeInt.num_cores):#run the process if true
                        self.logger.debug('(JOB>>>WORKER) ip: %s, port: %d'
                                          % (NodeInt.ip, NodeInt.port))
                        job.from_ip = self.ip
                        job.from_port = self.port
                        job_added = NodeInt.add_job(job)
                        if (job_added==True):
                            job_placed = True
                            break
                        else:
                            continue
                self.interfaces_lock.release()
                
            #chekc if job found a home
            if (job_placed==False):
                previous_job = job
                #self.logger.debug('(WAITING) waiting for a result to come in')
                self.result_added.wait()
                self.result_added.clear()
            else:
                previous_job = None
                continue   
            
    #move the results to the nodes queue
    def job_manager_processor(self):
        while (True):
            job = self.jobManager.get_result()
            if (job.from_ip==None and job.from_port==None):
                #self.logger.debug('added job to result_queue')
                self.result_queue.put(job)
            else:
                #self.logger.debug('added job to head node')
                job.finished = True
                intercom.post_job(job.from_ip, job.from_port, job)
            self.result_added.set()
            
    #process the jobs commming into the node
    def job_processor(self):
        self.logger.debug('in the job processor thread')
        while (True):
            sc = self.get_server_context()
            job_element = sc.job_queue.get()
            sc.job_queue_lock.acquire()
            sc.job_queue_count-=1
            sc.job_queue_lock.release()
            #the job submitted by the user
            job = Job.BaseJob()
            job.job_from_dictionary(job_element)
            
            if (job.finished==True):
                #add as a result
                #self.logger.debug('(result_queue<<<JOB PROC) got job')
                self.result_queue.put(job)
                self.result_added.set()
                continue
            else:
                #add as a job
                #self.logger.debug('(job_queue<<<JOB PROC) got job')
                self.add_job(job)
            
    
    #process things such as node interfaces and messages    
    def general_processor(self):
        self.logger.debug('in the processor thread')
        while(True):
            general_element = self.request_general_elements().get()
            self.logger.debug(general_element)
            
            if (general_element['type']==ElementTypes.slave_node_recv):
                
                node_data = general_element['json_data']
                node_interface = Interfaces.NodeInterface()
                
                #update the nodes counts. This means that the node
                #is up to date.
                node_interface.ip = node_data['ip']
                node_interface.port = node_data['port']
                node_interface.update_info()
                
                #update the interfaces list
                self.interfaces_lock.acquire()
                self.interfaces.append(node_interface)
                self.interfaces_lock.release()
                
                self.logger.debug('(HEAD(%d)<<<NODE INTERFACE) ip: %s, port: %d'
                                  % (self.port,node_interface.ip,node_interface.port))
                
                self.logger.debug('(IFL) interfaces: %s' % self.interfaces)
                
            else:
                self.logger.debug('ElementTypes does not contain: %s' % general_element)
                
    
    def add_job(self, job):
        self.job_queue.put(job)
        
    def get_result(self):
        return self.result_queue.get()
    
    def close_node(self):
        self.logger.debug('closing the node')
        self.request_close_server()
        self.REST_thread.join()
        
    def request_close_server(self):
        self.logger.debug('closing the server')
        intercom.close_server(self.ip, self.port) #close this node's server
        
    def get_server_context(self):
        return _RESTEndpoints.sc
    
    def request_general_elements(self):
        return self.get_server_context().general_queue
    
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
        
        
        
        
