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
    
    def __init__(self,):
        self.num_cores = multiprocessing.cpu_count()
        self.executor = concurrent.futures.ProcessPoolExecutor(self.num_cores)
        
        self.tasks = []
        
    def submit(self, task):
        self.tasks[self.executor.submit(task)]
        
    def set_num_cores(self, num_cores):
        self.num_cores = num_cores
        
    def set_executor(self, executor=concurrent.futures.ProcessPoolExecutor()):
        self.executor = executor
        
    def as_completed(self):
        return concurrent.futures.as_completed(self.tasks)        
    
    