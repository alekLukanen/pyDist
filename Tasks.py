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
def caller_helper(work_item):
    #unpickle the users function here
    work_item.unpickleInnerData()

    #call the users function
    work_item.set_result(work_item.fn(*work_item.args, **work_item.kwargs))
    work_item.set_ran()

    #repickle the function
    work_item.pickleInnerData()
    
    return work_item


class ClusterItem(object):

    def __init__(self):
        self.cluster_trace = []
        self.item_id = uuid.uuid4()
        self.interface_id = None


class WorkerItem(ClusterItem):
    
    def __init__(self, fn, args, kwargs):
        ClusterItem.__init__(self)

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.flag = None
        self.id = None

        self.ran = False
        self.result = None
        self._done_callbacks = []

        self._pickled_inner = False

    def set_ran(self):
        self.ran = True

    def set_result(self, result):
        self.result = result

    def pickleVariable(self, var):
        return pickleFunctions.createPickleServer(var)

    def unpickleVariable(self, var):
        return pickleFunctions.unPickleServer(var)

    def pickleInnerData(self):
        if not self._pickled_inner:
            self.fn = self.pickleVariable(self.fn)
            self.args = self.pickleVariable(self.args)
            self.kwargs = self.pickleVariable(self.kwargs)
            self.flag = self.pickleVariable(self.flag)
            self.id = self.pickleVariable(self.id)
            self.ran = self.pickleVariable(self.ran)
            self.result = self.pickleVariable(self.result)
            self._done_callbacks = self.pickleVariable(self._done_callbacks)

            self._pickled_inner = True

    def unpickleInnerData(self):
        if self._pickled_inner:
            self.fn = self.unpickleVariable(self.fn)
            self.args = self.unpickleVariable(self.args)
            self.kwargs = self.unpickleVariable(self.kwargs)
            self.flag = self.unpickleVariable(self.flag)
            self.id = self.unpickleVariable(self.id)
            self.ran = self.unpickleVariable(self.ran)
            self.result = self.unpickleVariable(self.result)
            self._done_callbacks = self.unpickleVariable(self._done_callbacks)

            self._pickled_inner = False

    def pickle(self):
        pickle = pickleFunctions.createPickleServer(self)
        return pickle

    def __str__(self):
        return f'item_id: {self.item_id}, id(user defined): {self.id}, ran: {self.ran}, result: {self.result}'


class VariableItem(ClusterItem):
    
    def __init__(self, variable, ip, port):
        ClusterItem.__init__(self)
        self.variable = variable
        self.ip = ip
        self.port = port


#the base task will be used as a simple version of the full task.
class Task(object):
    #states:
    #   CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED, RUNNING,
    
    def __init__(self, fn, args, kwargs):
        self.work_item = WorkerItem(fn, args, kwargs) #cluster facing
        self.future = concurrent.futures._base.Future() #user facing
        
    def update(self, work_item):
        self.work_item = work_item
        self.future.set_result(self.work_item.result)

    def pickle(self):
        pickle = pickleFunctions.createPickleServer(self.work_item)
        return pickle
    
    def createDictionary(self):
        return {'data': self.pickle()}
    
    def __str__(self):
        return self.work_item.__str__()
    
if __name__ == '__main__':
    task = Task()
    task.fn = 123
    print ('task: ', task)
    task.pickleFnOnly()
    print ('task.fn: ', task.fn)
    task.unpickleFnOnly()
    print ('task.fn: ', task.fn)
    
    
        