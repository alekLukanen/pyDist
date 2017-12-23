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
        self.num_running = 0
        self.executor = concurrent.futures.ProcessPoolExecutor(self.num_cores)
        
        #futures object that contains the task
        self.tasks = []
        
        #these are the Task object themselves not
        #the futures objects rapped around them.
        self.user_tasks = []
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
        self.queued_tasks.append(task)
        
    #update a task for viewing by the user 
    def update_task_by_id(self, task):
        for task_sub in self.user_tasks:
            if (task_sub.task_id==task.task_id):
                self.user_tasks.remove(task_sub)
                self.user_tasks.append(task)
                return True
        return False
    
    def remove_task_from_task_list_by_id(self, task):
        for future in self.tasks:
            if (future.done()==True or future.running()==False):
                if (future.result().task_id==task.task_id):
                    self.tasks.remove(future)
                    return True
        return False
    
    