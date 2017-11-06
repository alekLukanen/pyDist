#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 16:37:22 2017

@author: alek
"""

import concurrent.futures
import multiprocessing

class TaskManager(object):
    
    def __init__(self,):
        self.num_cores = multiprocessing.cpu_count()
        self.executor = concurrent.futures.ProcessPoolExecutor()
        
        self.tasks = []
        
    def set_num_cores(self, num_cores):
        self.num_cores = num_cores
        
    def set_executor(self, executor=concurrent.futures.ProcessPoolExecutor()):
        self.executor = executor
        
    def as_completed(self):
        
        
        
        