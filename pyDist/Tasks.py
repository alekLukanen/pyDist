#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 21:16:01 2017

@author: lukanen
"""

from pyDist import pickleFunctions, Items
import concurrent.futures


def caller_helper(work_item):
    #unpickle the users function here
    work_item.unpickleInnerData()

    #call the users function
    work_item.set_result(work_item.fn(*work_item.args, **work_item.kwargs))
    work_item.set_ran()

    #repickle the function
    work_item.pickleInnerData()
    
    return work_item


#the base task will be used as a simple version of the full task.
class Task(object):
    #states:
    #   CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED, RUNNING,
    
    def __init__(self, fn, args, kwargs):
        self.work_item = Items.WorkerItem(fn, args, kwargs) #cluster facing
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
