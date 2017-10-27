#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 14:58:52 2017

@author: lukanen
"""
from queue import Queue
from threading import Event, Lock
import logging
import sys
import json
import JobManager as JM
from Job import JobRunner

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("flask").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)
class ServerContext(object):
    
    def __init__(self):
        self.node_ref = None
        
        self.general_queue = Queue(0) #all tasks submitted here
        self.job_queue = Queue(0) #user jobs submitter here
        self.results_queue = Queue(0)
        
        self.running_jobs = []
        
        self.masters_lock = Lock()
        self.slaves_lock = Lock()
        self.credentials_lock = Lock()
        self.past_messages_lock = Lock()
        
        self.server_ended_event = Event()
        self.server_ended_event.clear()
        
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)s - %(funcName)20s() ] - %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
        self.logger = logging.getLogger()
    
    def get_node_info_by_index(self, node_index):
        return json.dumps( self.slaves[node_index] )
        
    def get_node_info(self):
        node_dictionary = self.node_ref.convert_to_dictionary()
        return json.dumps(node_dictionary)
    
    def get_node_counts(self):
        num_cores = self.node_ref.jobManager.num_processors
        num_running = len(self.node_ref.jobManager.running_job_dictionary)
        dictionary = {'num_cores':num_cores, 'num_running': num_running}
        return json.dumps( dictionary )
        
    def add_general_element(self, general_element):
        self.logger.debug('adding a general element')
        ##CONTROL LOGIC HERE
        self.general_queue.put(general_element)
        
    def add_message_element(self, message_element):
        self.logger.debug('adding a message element')
        ##CONTROL LOGIC HERE
        self.message_queue.put(message_element)
        
    def add_job_element(self, job_element):
        self.job_queue.put(job_element)
        
    def recieved_data(self,data_type):
        self.server_recieved_data_event.set()
        
    def server_ended(self):
        self.server_ended_event.set()
        
class ElementTypes:
    slave_node_recv = 'slave_node_recv'
    master_node_recv = 'master_node_recv'
    job_recv = 'job_recv'