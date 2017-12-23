#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 12:27:31 2017

@author: alek
"""

import asyncio
lp = asyncio.get_event_loop()
if (lp.is_closed()==True):
    print ('the current eventloop was closed, a new one was created')
    lp_temp = asyncio.new_event_loop()
    asyncio.set_event_loop(lp_temp)

from aiohttp import web
import json
import logging
import sys

import Interfaces
import endpoints
import Tasks
import pickleFunctions    
import TaskManager

logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
class ClusterNode(object):
    
    def __init__(self):
        logging.basicConfig(format='%(name)-12s:%(lineno)-3s | %(levelname)-6s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
        self.interface = Interfaces.NodeInterface()
        self.taskManager = TaskManager.TaskManager()
        
        self.user_interfaces = []
        
        self.server_interfaces = []
        self.client_interfaces = []
        
        self.server_loop = asyncio.get_event_loop()
        self.io_loop = asyncio.new_event_loop()
        
        self.app = web.Application(loop=self.server_loop)
        self.app.router.add_route('GET', '/', endpoints.index)
        self.app.router.add_route('GET', '/counts', endpoints.counts)
        self.app.router.add_route('GET', '/getTaskList', endpoints.getTaskList)
        self.app.router.add_route('POST', '/addTask', endpoints.addTask)
        self.app.router.add_route('POST', '/addStringMessage', endpoints.addStringMessage)
        
    ###NODE INFO CODE ####################    
    def get_counts(self):
        num_cores = self.interface.num_cores
        num_tasks_in_user_tasks = len(self.taskManager.user_tasks)
        num_tasks_in_running_list = len(self.taskManager.tasks)
        dictionary = {'num_tasks_in_user_tasks': num_tasks_in_user_tasks
                      , 'num_tasks_in_running_array': num_tasks_in_running_list
                      , 'num_cores':num_cores}
        return json.dumps( dictionary )
    
    def get_task_list(self):
        dictionary = {'data': pickleFunctions.pickleListServer(self.taskManager.user_tasks)}
        return json.dumps( dictionary )
    ###################################
        
    def boot(self, ip, port):
        endpoints.node = self #give the endpoints a reference to this object
        self.interface.ip = ip
        self.interface.port = port
        web.run_app(self.app, host=self.interface.ip, port=self.interface.port)
        
    def get_address(self):
        return "http://%s:%d" % (self.interface.ip, self.interface.port)
    
    ###TASK CODE ######################
    def sign_task(self, task_object):
        task_object.cluster_trace.append(self.interface.get_signature())
    
    def add_existing_task_async(self, task_object):
        self.logger.debug('adding_existing_task_async()')
        self.sign_task(task_object)
        
        #always pickle inner task data here
        task_object.pickleInnerData()
        
        if (len(self.taskManager.tasks)<self.taskManager.num_cores):
            task = self.taskManager.executor.submit(Tasks.caller_helper, task_object)
            task.add_done_callback(self.task_finished_callback)
            self.taskManager.submit(task)
        else:
            self.logger.debug('task was not added because queue is already full')
        self.taskManager.user_tasks.append(task_object)
    
    def add_existing_task(self, task):
        self.logger.debug('add_existing_task()')
        task_object = pickleFunctions.unPickleServer(task['data'])
        self.server_loop.call_soon_threadsafe(self.add_existing_task_async, task_object)
        return True
    
    def task_finished_callback(self, future):
        self.logger.debug('task_finished_callback() result: %s' % future)
        #get the task from future and unpickle the inside of the task
        returned_task = future.result()
        returned_task.unpickleInnerData()
        #here is where the taskmanager is udated based on the 
        #tasks finished callback.
        #subract one from the taskmanagers couter
        #add a done result to the task
        #update the task in user_tasks with the result
        #remove the future from the task list, this keeps the futures list small
        self.taskManager.add_finished_task(returned_task.task_id)
        t_updated = self.taskManager.update_task_by_id(returned_task)
        t_removed = self.taskManager.remove_task_from_task_list_by_id(returned_task)
        #show warning messages when necessary
        if (t_updated!=True):
            self.logger.warning('A TASK FAILED TO UPDATE')
        if (t_removed!=True):
            self.logger.warning('A FUTURE FAILED TO BE REMOVED')
        
    ####################################
    
    ###MESSAGE CODE ####################
    def add_string_message(self, message):
        self.logger.debug('add_message()')
        msg = pickleFunctions.unPickleServer(message['data'])
        self.logger.debug('RECIEVED MESSAGE: ', msg)
        
    #####################################
    
    #EXECUTOR METHODS HERE####################
    
    #submit a new job here
    #this is where a new task needs to be created
    def submit(self, fn, *args, **kwards):
        task = Tasks.Task()
        
        self.logger.debug('submit')
        
    def map(self, func, *iterables, timeout=None, chuncksize=1):
        self.logger.debug('map function')
        
    def shutdown(self, wait=True):
        self.logger.debug('shutdown()')
        self.server_loop.call_soon_threadsafe(self.server_loop.stop)
    
    ##########################################
    
    
        
if __name__=='__main__':
    print ('starting a ClusterExecutorNode...')
    node = ClusterNode()
    node.boot('0.0.0.0', 9000)
    
    