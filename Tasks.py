#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 21:16:01 2017

@author: lukanen
"""
import NodeInterface
import pickleFunctions
import concurrent.futures

class WorkerItem(object):
    
    def __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


class VariableItem(object):
    
    def __init__(self, variable, ip, port):
        self.variable = variable
        self.ip = ip
        self.port = port

#the base task will be used as a simple version of the full task.
class Task(concurrent.futures.Future):
    
    def __init__(self):
        concurrent.futures.Future.__init__(self)
        self.node_interface = None
        
        self.from_ip = None
        self.from_port = None
        self.cluster_trace = []
        
        self.job_id = None
        
    def convert_obj_to_dictionary(self, obj):
        if (obj!=None):
            return obj.convert_to_dictionary()
        return None
    
    def convert_to_dictionary(self):
        dictionary = {
                'node_interface': self.convert_obj_to_dictionary(self.node_interface),
                'from_ip': self.from_ip,
                'from_port': self.from_port,
                'cluster_trace': [self.convert_obj_to_dictionary(node) for node in self.cluster_trace],
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
            
        self.from_ip = dictionary['from_ip'] if 'from_ip' in dictionary else None
        self.from_port = dictionary['from_port'] if 'from_port' in dictionary else None
            
        if ('cluster_trace' in dictionary):
            for node_dict in dictionary['cluster_trace']:
                node = NodeInterface.NodeInterface()
                node.create_from_dictionary(node_dict)
                self.cluster_trace.append(node)
        else:
            self.cluster_trace = []
        
        self.job_id = pickleFunctions.unPickle(dictionary['job_id'].encode('latin1')) if 'job_id' in dictionary else ''
        
    
    
if __name__ == '__main__':
    task = Task()
    task.cancelled = True
    serial_task = task.convert_to_dictionary()
    print ('serial_task %s' % serial_task)
    new_task = Task()
    new_task.create_from_dictionary(serial_task)
    
        