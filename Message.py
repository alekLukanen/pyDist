#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 22:20:15 2017

@author: lukanen
"""

class StackMessage(object):
    
    def __init__(self, data=[]):
        self.data = data
        self.cluster_trace = []
        self.name = 'MessageBase'
        
    def addItem(self, item):
        self.data.append(item)
        
    def getItem(self):
        return self.data.pop()
    
    def getLength(self):
        return len(self.data)
    
    def __str__(self):
        return ("len(data): %d, len(cluster_trace)" % (len(self.data),len(self.cluster_trace)))

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
            
    
if __name__ == '__main__':
    print ('Message testing...')
    
    print ('stack message')
    s_msg = StackMessage(data=[1,2,3])
    s_msg.addItem(4)
    
    for _ in range(0, s_msg.getLength()):
        print ('s_msg.pop(): ', s_msg.getItem())
        
    print ('string message')
    str_msg = StringMessage(message='this is the message')
    print ('str_msg: ', str_msg)
    
    