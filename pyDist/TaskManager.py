#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 16:37:22 2017

@author: alek
"""

import concurrent.futures
import multiprocessing
from pyDist import Tasks

import logging
import sys

#this is a basic task manager object used
#to contain the 
class TaskManager(object):
    
    #the TaskManager object is initialized with
    #   self.num_cores - the number of cores in the computer
    #   self.executor - the process pool executor used by the manager
    #   self.tasks - the tasks submitted to the executor
    def __init__(self):
        
        logging.basicConfig(format='%(name)-12s:%(lineno)-3s | %(levelname)-8s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
        self.num_cores = multiprocessing.cpu_count()
        self.num_running = 0
        self.executor = concurrent.futures.ProcessPoolExecutor(self.num_cores)
        
        #futures object that contains the task
        self.tasks = []
        
        #these are the Task object themselves not
        #the futures objects rapped around them.
        self.queued_tasks = []
        self.tasks_finished = []
        
    #subit the task to the executor and save task
    def submit(self, task):
        self.tasks.append(task)
        
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
        
    def add_finished_task(self, task):
        self.tasks_finished.append(task)
        
    #update a task for viewing by the test_nodeEndpoints
    def update_task_by_id(self, task):
        for task_sub in self.user_tasks:
            if (task_sub.task_id==task.task_id):
                self.user_tasks.remove(task_sub)
                self.user_tasks.append(task)
                return True
        return False
    
    def remove_work_item_from_task_list_by_id(self, work_item):
        for future in self.tasks:
            if future.done()==True or future.running()==False:
                if future.result().item_id == work_item.item_id:
                    self.tasks.remove(future)
                    return True
        return False
    
    def run_queued_task(self, node):
        if (len(self.queued_tasks)>0):
            task_object = self.queued_tasks.pop()
            self.logger.debug('running queued task: %s' % task_object.task_id)
            task = self.executor.submit(Tasks.caller_helper, task_object)
            task.add_done_callback(node.work_item_finished_callback)
            self.submit(task)
            self.user_tasks.append(task_object)
            return True
        else:
            return False
