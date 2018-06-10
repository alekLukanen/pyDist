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
import threading

FIRST_COMPLETED = 'FIRST_COMPLETED'
FIRST_EXCEPTION = 'FIRST_EXCEPTION'
ALL_COMPLETED = 'ALL_COMPLETED'
_AS_COMPLETED = '_AS_COMPLETED'

# Possible future states (for internal use by the futures package).
PENDING = 'PENDING'
RUNNING = 'RUNNING'
# The future was cancelled by the user...
CANCELLED = 'CANCELLED'
# ...and _Waiter.add_cancelled() was called by a worker.
CANCELLED_AND_NOTIFIED = 'CANCELLED_AND_NOTIFIED'
FINISHED = 'FINISHED'

_TASK_STATES = [
    PENDING,
    RUNNING,
    CANCELLED,
    CANCELLED_AND_NOTIFIED,
    FINISHED
]

#use this function to call the users function
def caller_helper(task):
    #unpickle the users function here
    task.unpickleInnerData()
    #need to set the condition for this unpickle(new) object
    task.new_condition()
    #call the users function
    task.set_result(task.fn(*task.args, **task.kwargs))
    #repickle the function
    task.pickleInnerData()
    task.set_run()
    task.remove_condition()
    
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
class Task(concurrent.futures._base.Future):
    #states:
    #   CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED, RUNNING,
    
    def __init__(self):
        #concurrent.futures.Future.__init__(self)
        self.cluster_trace = []
        self.task_id = uuid.uuid4()
        self.interface_id = None
        
        self.flag = None
        self.id = None
        self.fn = None
        self.args = ()
        self.kwargs = {}
        
        self._condition = threading.Condition()
        self._state = PENDING
        self._result = None
        self._exception = None
        self._waiters = []
        self._done_callbacks = []
        self._pickled_inner = False
        
    def update(self, task):
        self.cluster_trace = task.cluster_trace
        self.task_id = task.task_id
        self.interface_id = task.interface_id
        self.flag = task.flag
        self.id = task.id
        self.fn = task.fn
        self.args = task.args
        self.kwargs = task.kwargs
        
        self._state = task._state
        self._result = task._result
        self._exception = task._exception
        self._waiters = task._waiters
        self._done_callbacks = task._done_callbacks
        self._pickled_inner = task._pickled_inner
        
    def new_condition(self):
        self._condition = threading.Condition()
        
    def remove_condition(self):
        self._condition = None
        
    def pickled_inner(self):
        return self._pickled_inner
        
    def exception(self):
        return self._exception
        
    def set_exception(self, exception):
        self._exception = exception
        
    def set_run(self):
        self._state = FINISHED
        
    def pickleVariable(self, var):
        return pickleFunctions.createPickleServer(var)
        
    def unpickleVariable(self, var):
        return pickleFunctions.unPickleServer(var)
    
    def pickleInnerData(self):
        if (self._pickled_inner==False):
            self.fn = self.pickleVariable(self.fn)
            self.args = self.pickleVariable(self.args)
            self.kwargs = self.pickleVariable(self.kwargs)
            self._result = self.pickleVariable(self._result)
            self._pickled_inner = True
    
    def unpickleInnerData(self):
        if (self._pickled_inner==True):
            self.fn = self.unpickleVariable(self.fn)
            self.args = self.unpickleVariable(self.args)
            self.kwargs = self.unpickleVariable(self.kwargs)
            self._result = self.unpickleVariable(self._result)
            self._pickled_inner = False
    
    def pickle(self):
        con = self._condition
        self._condition = None
        pickle = pickleFunctions.createPickleServer(self)
        self._condition = con
        return pickle
    
    def createDictionary(self):
        return {'data': self.pickle()}
        
    def convert_obj_to_dictionary(self, obj):
        if (obj!=None):
            return obj.convert_to_dictionary()
        return None
    
    def __str__(self):
        return ("task_id: %s, interface_id: %s, id(userDef): %s, cluster_trace: %s" 
                % (self.task_id, self.interface_id, self.id, self.cluster_trace))
    
if __name__ == '__main__':
    task = Task()
    task.fn = 123
    print ('task: ', task)
    task.pickleFnOnly()
    print ('task.fn: ', task.fn)
    task.unpickleFnOnly()
    print ('task.fn: ', task.fn)
    
    
        