#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 15:14:10 2017

@author: alek
"""

import pickleFunctions
from Node import BaseNode

class BaseJob(object):
    
    def __init__(self):
        self.file_name = ''
        self.num_instances = 1
        self.root_node = None
        self.data = None #can be any python object
        self.job_id = 'example_id'
        self.function_name = 'no_function'
        self.arguements = []
        self.return_value = ''
        self.finished = False
        
    def convert_root_node(self):
        if (self.root_node==None):
            return None
        else:
            return self.root_node.convert_to_dictionary()

    def convert_to_dictionary(self):
        dictionary = {
                'file_name': self.file_name,
                'num_instances': self.num_instances,
                'root_node': self.convert_root_node(),
                'data': pickleFunctions.createPickle(self.data).decode('utf-8'),
                'job_id': self.job_id,
                'function_name': self.function_name,
                'arguements': self.arguements,
                'return_value': self.return_value,
                'finished': self.finished
                }
        return dictionary
    
    def job_from_dictionary(self, data):
        self.file_name = data['file_name'] if 'file_name' in data else ''
        self.num_instances = data['num_instances'] if 'num_instances' in data else 0
        root_node = BaseNode()
        root_node.BaseNode_from_dictionary(data['root_node'])
        self.root_node = root_node
        self.data = pickleFunctions.unPickle(data['data'].encode()) if 'data' in data else ''
        self.job_id = data['job_id'] if 'job_id' in data else ''
        self.function_name = data['function_name'] if 'function_name' in data else ''
        self.arguements = data['arguements'] if 'arguements' in data else ()
        self.return_value = data['return_value'] if 'return_value' in data else ''
        self.finished = data['finished'] if 'finished' in data else False

class JobServer(BaseJob):
    
    def __init__(self):
        BaseJob.__init__(self)
        #the id of the client
        self.sent_to_node = -1 #index of node
        self.run = False #if true the node runs the job
    
    def convert_to_dictionary(self):
        dictionary = {
                'file_name': self.file_name,
                'num_instances': self.num_instances,
                'root_node': self.convert_root_node(),
                'data': pickleFunctions.createPickle(self.data).decode('utf-8'),
                'job_id': self.job_id,
                'function_name': self.function_name,
                'arguements': self.arguements,
                'return_value': self.return_value,
                'finished': self.finished,
                'sent_to_node': self.sent_to_node,
                'run': self.run
                }
        return dictionary
        
    def job_from_dictionary(self, data):
        self.file_name = data['file_name'] if 'file_name' in data else ''
        self.num_instances = data['num_instances'] if 'num_instances' in data else 0
        root_node = BaseNode()
        root_node.BaseNode_from_dictionary(data['root_node'])
        self.root_node = root_node
        self.data = pickleFunctions.unPickle(data['data'].encode()) if 'data' in data else ''
        self.job_id = data['job_id'] if 'job_id' in data else ''
        self.function_name = data['function_name'] if 'function_name' in data else ''
        self.arguements = data['arguements'] if 'arguements' in data else ()
        self.return_value = data['return_value'] if 'return_value' in data else ''
        self.finished = data['finished'] if 'finished' in data else False
        self.sent_to_node = data['sent_to_node'] if 'sent_to_node' in data else -1
        self.run = data['run'] if 'run' in data else False
        
        
class JobRunner(BaseJob):
    
    def __init__(self):
        JobServer.__init__(self)
        self.node_index = -1
        self.node_id = -1
        self.job_manager_id = -1
        self.processor = None
        
    def convert_to_dictionary(self):
        dictionary = {
                'file_name': self.file_name,
                'num_instances': self.num_instances,
                'node_index': self.node_index,
                'root_node': self.convert_root_node(),
                'data': pickleFunctions.createPickle(self.data).decode('utf-8'),
                'job_id': self.job_id,
                'function_name': self.function_name,
                'arguements': self.arguements,
                'return_value': self.return_value,
                'finished': self.finished,
                'sent_to_node': self.sent_to_node,
                'run': self.run,
                'job_manager_id': self.job_manager_id,
                'processor': True if self.processor!=None else False
                }
        return dictionary
        
    def job_from_dictionary(self, data):
        self.file_name = data['file_name'] if 'file_name' in data else ''
        self.num_instances = data['num_instances'] if 'num_instances' in data else 0
        root_node = BaseNode()
        root_node.BaseNode_from_dictionary(data['root_node'])
        self.root_node = root_node
        self.data = pickleFunctions.unPickle(data['data'].encode()) if 'data' in data else ''
        self.job_id = data['job_id'] if 'job_id' in data else ''
        self.function_name = data['function_name'] if 'function_name' in data else ''
        self.arguements = data['arguements'] if 'arguements' in data else ()
        self.return_value = data['return_value'] if 'return_value' in data else ''
        self.finished = data['finished'] if 'finished' in data else False
        self.sent_to_node = data['sent_to_node'] if 'sent_to_node' in data else -1
        self.run = data['run'] if 'run' in data else False
        self.node_index = data['node_index'] if 'node_index' in data else 0
        self.job_manager_id = data['job_manager_id'] if 'job_manager_id' in data else -1
        self.processor = None
        
        
        
        
        
        
        