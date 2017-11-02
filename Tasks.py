#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 21:16:01 2017

@author: lukanen
"""
import NodeInterface
import pickleFunctions

#the base task will be used as a simple version of the full task.
class BaseTask(object):
    
    def __init__(self):
        self.node_interface = None
        
        self.file_name = None
        self.function_name = None
        
        self.arguements = ()
        self.return_value = None
        self.exception = None
        
        self.cluster_trace = []
        self.finished = False
        
        self.job_id = None
        
    def convert_obj_to_dictionary(self, obj):
        if (obj!=None):
            return obj.convert_to_dictionary()
        return None
    
    def convert_to_dictionary(self):
        dictionary = {
                'node_interface': self.convert_obj_to_dictionary(self.node_interface),
                'file_name': self.file_name,
                'function_name': self.function_name,
                'arguements': pickleFunctions.createPickle(self.arguements).decode('latin1'),
                'return_value': pickleFunctions.createPickle(self.return_value).decode('latin1'),
                'exception': pickleFunctions.createPickle(self.exception.decode('latin1')),
                'cluster_trace': [self.convert_obj_to_dictionary(node) for node in self.cluster_trace],
                'finished': self.finished,
                'job_id': pickleFunctions.createPickle(self.job_id).decode('latin1')
                }
        return dictionary
    
    
    def create_from_dictionary(self, dictionary):
        if ('node_interface' in dictionary):
            self.node_interface = NodeInterface.NodeInterface()
            self.node_interface.create_from_dictionary(dictionary['node_interface'])
        else:
            self.node_interface = None
            
        self.file_name = dictionary['file_name'] if 'file_name' in dictionary else None
        self.function_name = dictionary['function_name'] if 'function_name' in dictionary else None
        self.exception = pickleFunctions.unPickle(dictionary['exception'].encode('latin1')) if 'exception' in dictionary else None
        
        self.arguements = pickleFunctions.unPickle(dictionary['arguements'].encode('latin1')) if 'arguements' in dictionary else ()
        self.return_value = pickleFunctions.unPickle(dictionary['return_value'].encode('latin1')) if 'return_value' in dictionary else None
        
        if ('cluster_trace' in dictionary):
            for node_dict in dictionary['cluster_trace']:
                node = NodeInterface.NodeInterface()
                node.create_from_dictionary(node_dict)
                self.cluster_trace.append(node)
        else:
            self.cluster_trace = []
        
        self.finished = dictionary['finished'] if 'finished' in dictionary else False
        
        self.job_id = pickleFunctions.unPickle(dictionary['job_id'].encode('latin1')) if 'job_id' in dictionary else ''
        
        
class Task(BaseTask):
    
    def __init__(self):
        BaseTask.__init__(self)
        self.cancel = False
        self.cancelled = False
        self.callbacks = []
        
    def cancel(self):
        print ('cancel()')
        self.cancel = True
        #try and cancle the process here
        return self.cancelled
        
    def cancelled(self):
        print ('cancelled()')
        return self.cancelled
    
    def done(self):
        print ('done()')
        return self.finished
    
    def result(self):
        print ('result()')
        return self.return_value
    
    def exception(self):
        print ('exception()')
        return self.exception
    
    def add_done_callback(self, fn):
        print ('add_done_callback()')
        self.callbacks.append(fn)
        
    #other functions here
        
    
    
    
        