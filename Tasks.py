#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 21:16:01 2017

@author: lukanen
"""
import NodeInterface
import pickleFunctions
import concurrent.futures

#use this function to call the users function
def caller_helper(task):
    print ('caller_helper(%s)' % task)
    
    #unpickle the users function here
    task.unpickleFnOnly()
    
    #call the users function
    task.set_result(task.fn())
    
    #repickle the function
    task.pickleFnOnly()
    
    return task
    

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
        
        self.fn = None
        self.args = ()
        self.kwargs = {}
        
        self._result = None
        
    def result(self):
        return self._result
    
    def set_result(self, result):
        self._result = result
        
    def pickleFnOnly(self):
        self.fn = pickleFunctions.createPickleServer(self.fn)
        
    def unpickleFnOnly(self):
        self.fn = pickleFunctions.unPickleServer(self.fn)
    
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
    task.fn = 123
    print ('task: ', task)
    task.pickleFnOnly()
    print ('task.fn: ', task.fn)
    task.unpickleFnOnly()
    print ('task.fn: ', task.fn)
    
    
        