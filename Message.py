#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 22:20:15 2017

@author: lukanen
"""

class MessageBase(object):
    
    def __init__(self):
        self.data = []
        self.cluster_trace = []
        self.name = 'MessageBase'
        
    def addItem(self, item):
        self.data.append(item)
        
    def getItem(self):
        return self.data.pop()

class StringMessage(object):
    
    def __init__(self, message=''):
        self.message = message
        
    def convert_to_dictionary(self):
        dictionary = {
                'message': self.message
                }
        return dictionary
        
    def create_from_dictionary(self, dictionary):
        self.message = dictionary['message'] if 'message' in dictionary else None
        
    def __str__(self):
        return 'message: %s' % self.message
            