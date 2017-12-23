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
#class Task(concurrent.futures.Future):
class Task(object):
    
    def __init__(self):
        #concurrent.futures.Future.__init__(self)
        self.cluster_trace = []
        self.task_id = None
    
    def pickle(self):
        return pickleFunctions.createPickleServer(self)
    
    def createDictionary(self):
        return {'data': self.pickle()}
        
    def convert_obj_to_dictionary(self, obj):
        if (obj!=None):
            return obj.convert_to_dictionary()
        return None
    
    def __str__(self):
        return ("task_id: %s, cluster_trace: %s" % (self.task_id, self.cluster_trace))
    
if __name__ == '__main__':
    task = Task()
    print ('task: ', task)
    
    
        