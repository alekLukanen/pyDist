#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 21:16:01 2017

@author: lukanen
"""
import NodeInterface
import pickleFunctions

class BaseTask(object):
    
    def __init__(self):
        self.node_interface = None
        
        self.file_name = None
        self.function_name = None
        
        self.arguements = ()
        self.return_value = None
        
        self.cluster_trace = []
        self.finished = False
        
    def convert_obj_to_dictionary(self, obj):
        if (obj!=None):
            return obj.convert_to_dictionary()
        return None
    
    def convert_to_dictionary(self):
        dictionary = {
                'node_interface': self.convert_obj_to_dictionary(self.node_interface),
                'file_name': self.file_name,
                'function_name': self.function_name,
                'arguements': self.arguements,
                'return_value': self.return_value,
                'cluster_trace': [self.convert_obj_to_dictionary(node) for node in self.cluster_trace],
                'self.finished': self.finished
                }
        return dictionary
    
    def create_from_dictionary(self, dictionary):
        if ('node_interface' in dictionary):
            self.node_interface = NodeInterface.NodeInterface()
            self.node_interface.create_from_dictionary(dictionary['node_interface'])
        else:
            self.node_interface = None
            
        self.file_name = dictionary['file_name'] if 'file_name' in dictionary else ''
        self.function_name = dictionary['function_name'] if 'function_name' in dictionary else ''
        
        self.arguements = pickleFunctions.unPickle(dictionary['arguements'].encode('latin1')) if 'arguements' in dictionary else ()
        self.return_value = pickleFunctions.unPickle(dictionary['return_value'].encode('latin1')) if 'return_value' in dictionary else ''
        
        if ('cluster_trace' in dictionary):
            for node_dict in dictionary['cluster_trace']:
                node = NodeInterface.NodeInterface()
                node.create_from_dictionary(node_dict)
                self.cluster_trace.append(node)
        else:
            self.cluster_trace = []
            
        self.finished = dictionary['finished'] if 'finished' in dictionary else False
        
        
        
        