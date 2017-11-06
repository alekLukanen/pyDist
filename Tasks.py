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
        
        self.function = None
        
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
                'function': pickleFunctions.createPickle(self.function).decode('latin1'),
                'arguements': pickleFunctions.createPickle(self.arguements).decode('latin1'),
                'return_value': pickleFunctions.createPickle(self.return_value).decode('latin1'),
                'exception': pickleFunctions.createPickle(self.exception).decode('latin1'),
                'cluster_trace': [self.convert_obj_to_dictionary(node) for node in self.cluster_trace],
                'finished': self.finished,
                'job_id': pickleFunctions.createPickle(self.job_id).decode('latin1')
                }
        return dictionary
    
    
    def create_from_dictionary(self, dictionary):
        if ('node_interface' in dictionary):
            if (dictionary['node_interface']!=None):
                self.node_interface = NodeInterface.NodeInterface()
                self.node_interface.create_from_dictionary(dictionary['node_interface'])
            else:
                self.node_interface = None
        else:
            self.node_interface = None
            
        self.function = pickleFunctions.unPickle(dictionary['function'].encode('latin1')) if 'function' in dictionary else None
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
        
    def convert_to_dictionary(self):
        dictionary = {
                'cancel': self.cancel,
                'cancelled': self.cancelled,
                'callbacks': [callback.convert_to_dictionary() for callback in self.callbacks]
                }
        dictionary.update(super(Task, self).convert_to_dictionary())
        return dictionary
        
    def create_from_dictionary(self, dictionary):
        super(Task, self).create_from_dictionary(dictionary)
        self.cancel = dictionary['cancel'] if 'cancel' in dictionary else False
        self.cancelled = dictionary['cancelled'] if 'cancelled' in dictionary else False
        if ('callbacks' in dictionary):
            for callback in dictionary['callbacks']:
                task = Task()
                task.create_from_dictionary(callback)
                self.callbacks.append(task)
        
    #other functions here
    
    
    
if __name__ == '__main__':
    task = Task()
    task.cancelled = True
    serial_task = task.convert_to_dictionary()
    print ('serial_task %s' % serial_task)
    new_task = Task()
    new_task.create_from_dictionary(serial_task)
    
        