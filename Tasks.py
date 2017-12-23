#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 21:16:01 2017

@author: lukanen
"""
import Interfaces
import pickleFunctions
import concurrent.futures
import uuid

#use this function to call the users function
def caller_helper(task):
    #unpickle the users function here
    task.unpickleInnerData()
    #call the users function
    task.set_result(task.fn(*task.args, **task.kwargs))
    #repickle the function
    task.pickleInnerData()
    task.set_run()
    
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
        self.task_id = uuid.uuid4()
        self.user_id = None
        self.group_id = None
        
        self.flag = None
        self.id = None
        self.fn = None
        self.args = ()
        self.kwargs = {}
        
        self.__result = None
        self.__run = False
        self.__exception = None
        
        self.__pickled_inner = False
        
    def pickled_inner(self):
        return self.__pickled_inner
        
    def result(self):
        return self.__result
    
    def set_result(self, result):
        self.__result = result
        
    def exception(self):
        return self.__exception
        
    def set_exception(self, exception):
        self.__exception = exception
        
    def done(self):
        return self.__run
        
    def set_run(self):
        self.__run = True
        
    def pickleVariable(self, var):
        return pickleFunctions.createPickleServer(var)
        
    def unpickleVariable(self, var):
        return pickleFunctions.unPickleServer(var)
    
    def pickleInnerData(self):
        self.fn = self.pickleVariable(self.fn)
        self.args = self.pickleVariable(self.args)
        self.kwargs = self.pickleVariable(self.kwargs)
        self.__result = self.pickleVariable(self.__result)
        self.__pickled_inner = True
    
    def unpickleInnerData(self):
        self.fn = self.unpickleVariable(self.fn)
        self.args = self.unpickleVariable(self.args)
        self.kwargs = self.unpickleVariable(self.kwargs)
        self.__result = self.unpickleVariable(self.__result)
        self.__pickled_inner = False
    
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
    
    
        