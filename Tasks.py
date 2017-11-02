#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 21:16:01 2017

@author: lukanen
"""

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
    