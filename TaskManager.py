#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 16:37:22 2017

@author: alek
"""

import concurrent.futures
import multiprocessing

#this is a basic task manager object used
#to contain the 
class TaskManager(object):
    
    #the TaskManager object is initialized with
    #   self.num_cores - the number of cores in the computer
    #   self.executor - the process pool executor used by the manager
    #   self.tasks - the tasks submitted to the executor
    def __init__(self,):
        self.num_cores = multiprocessing.cpu_count()
        self.executor = concurrent.futures.ProcessPoolExecutor(self.num_cores)
        
        self.tasks = []
        
    #subit the task to the executor and save task
    def submit(self, task):
        self.tasks[self.executor.submit(task)]
        
    #set the number of processes to be used by the executor
    #TO DO - need to get this to update the executor with new process count
    def set_num_cores(self, num_cores):
        self.num_cores = num_cores
        
    #set the executor of the manager. defaults to process pool
    def set_executor(self, executor=concurrent.futures.ProcessPoolExecutor()):
        self.executor = executor
        
    #a generator that returns tasks as completed. 
    def as_completed(self):
        return concurrent.futures.as_completed(self.tasks)        
    
    