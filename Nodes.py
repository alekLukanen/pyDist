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
        logging.basicConfig(format='%(name)-12s:%(lineno)-3s | %(levelname)-8s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
        self.interface = Interfaces.NodeInterface()
        self.taskManager = TaskManager.TaskManager()
        self.interface.num_cores = self.taskManager.num_cores
        self.interface.num_running = 0
        self.interface.num_queued = 0
        
        self.interfaces = Interfaces.InterfaceHolder()
        
        self.server_loop = asyncio.get_event_loop()
        self.io_loop = asyncio.new_event_loop()
        
        self.task_added = True
        
        self.app = web.Application(loop=self.server_loop)
        self.app.router.add_route('GET', '/', endpoints.index)
        self.app.router.add_route('GET', '/counts', endpoints.counts)
        self.app.router.add_route('GET', '/nodeInfo', endpoints.nodeInfo)
        self.app.router.add_route('GET', '/getFinishedTaskList', endpoints.getFinishedTaskList)
        self.app.router.add_route('GET', '/getSingleTask', endpoints.getSingleTask)
        self.app.router.add_route('POST', '/addTask', endpoints.addTask)
        self.app.router.add_route('POST', '/addStringMessage', endpoints.addStringMessage)
        self.app.router.add_route('POST', '/connectUser', endpoints.connectUser)
        
    ###USER INTERACTION CODE##############
    
    ######################################
        
    ###NODE INFO CODE ####################    
    def get_counts(self):
        num_cores = self.taskManager.num_cores
        num_tasks_in_running_list = len(self.taskManager.tasks)
        num_tasks_in_queue_list = len(self.taskManager.queued_tasks)
        dictionary = {'num_tasks_running': num_tasks_in_running_list
                      , 'num_tasks_queue': num_tasks_in_queue_list
                      , 'num_cores':num_cores}
        return json.dumps( dictionary )
    
    def get_info(self):
        return json.dumps( self.interface.info() )
    
    def get_tasks_finished(self, params):
        user = self.interfaces.find_user_by_user_id(params['user_id'])
        if (user!=None):
            dictionary = {'data': pickleFunctions.pickleListServer(user.tasks_finished)}
            return json.dumps( dictionary )
        else:
            return json.dumps( {'data': [], 'error': 'no user for that user_id'} )
        
    async def get_a_finished_task(self, params):
        user = self.interfaces.find_user_by_user_id(params['user_id'])
        if (user!=None):
            await self.server_loop.run_in_executor(None
                    , self.interfaces.wait_for_first_finished_task_for_user, user)
            task = self.interfaces.find_finished_task_for_user(user)
            self.interfaces.reset_finished_event_for_user(user)
            if (task!=None):
                dictionary = {'data': task.pickle()}
                self.logger.debug('dictionary: %s' % dictionary)
                return json.dumps( dictionary )
            else:
                self.logger.warning('the task was of Nonetype')
                return json.dumps( {'data': None, 'error': 'task was none'} )
        else:
            return json.dumps( {'data': None, 'error': 'no user for that user_id'} )
        
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
    
    def add_existing_task_async(self, task):
        self.logger.debug('adding_existing_task_async()')
        task_object = pickleFunctions.unPickleServer(task['data'])
        
        #always pickle inner task data here
        task_object.pickleInnerData()
        self.logger.debug('task_object %s' % task_object)
        
        #add the task to the users submitted tasks array
        user = self.interfaces.find_user_by_user_id(task['user_id'])
        if (user!=None):
            task_object.interface_id = user.interface_id
            user.tasks_recieved.append(task_object)
        else:
            self.logger.warning('THE USER DOES NOT EXIST, TASK NOT ADDED')
            self.task_added = False
            return
        
        if (len(self.taskManager.tasks)<self.taskManager.num_cores):
            task = self.taskManager.executor.submit(Tasks.caller_helper, task_object)
            task.add_done_callback(self.task_finished_callback)
            self.taskManager.submit(task)
            self.logger.debug('task_object: %s' % task_object)
        else:
            self.taskManager.queued_tasks.append(task_object)
            self.logger.debug('task was not added because queue is already full')
        self.task_added = True
        return
    
    def run_task_from_user(self):
        if (len(self.taskManager.tasks)<self.taskManager.num_cores):
            user, task_object = self.interfaces.find_user_task()
            if (user==task_object==None):
                self.logger.debug('No users have tasks to perfom')
                return False
            future = self.taskManager.executor.submit(Tasks.caller_helper, task_object)
            future.add_done_callback(self.task_finished_callback)
            self.taskManager.submit(future)
            user.tasks_running.append(task_object.task_id)
            self.logger.debug('task_object: %s' % task_object)
            return True
        else:
            self.logger.debug('task was not run becuase no cores available')
            return False
        
    def add_task_to_user(self, task):
        self.logger.debug('adding_existing_task_async()')
        task_object = pickleFunctions.unPickleServer(task['data'])
        self.sign_task(task_object)
        
        #always pickle inner task data here
        task_object.pickleInnerData()
        self.logger.debug('task_object %s' % task_object)
        
        #add the task to the users submitted tasks array
        user = self.interfaces.find_user_by_user_id(task['user_id'])
        if (user!=None):
            task_object.interface_id = user.interface_id
            user.tasks_recieved.append(task_object)
        else:
            self.logger.warning('THE USER DOES NOT EXIST, TASK NOT ADDED')
            self.task_added = False
            return
        #set add bool and find user task to run
        self.task_added = True
        self.run_task_from_user()
    
    def add_existing_task(self, task):
        self.logger.debug('add_existing_task()')
        #self.server_loop.call_soon_threadsafe(self.add_existing_task_async, task)
        self.server_loop.call_soon_threadsafe(self.add_task_to_user, task)
        return json.dumps( {'task_added': self.task_added} )
    
    def task_finished_callback(self, future):
        self.logger.debug('task_finished_callback() result: %s' % future)
        #get the task from future and unpickle the inside of the task
        returned_task = future.result()
        returned_task.unpickleInnerData()
        returned_task.new_condition()
        #here is where the taskmanager is udated based on the 
        #tasks finished callback.
        #subract one from the taskmanagers couter
        #add a done result to the task
        #update the task in user_tasks with the result
        #remove the future from the task list, this keeps the futures list small
        t_updated = self.interfaces.update_task_in_user(returned_task) #self.taskManager.update_task_by_id(returned_task)
        t_removed = self.taskManager.remove_task_from_task_list_by_id(returned_task)
        t_added   = self.run_task_from_user()
        #show warning messages when necessary
        self.logger.debug('user.counts(): %s' 
                % self.interfaces.find_user_by_interface_id(returned_task.interface_id).counts())
        if (t_updated==False):
            self.logger.warning('A TASK FAILED TO UPDATE')
        if (t_removed==False):
            self.logger.warning('A FUTURE FAILED TO BE REMOVED')
        if (t_added==False):
            self.logger.debug('TASK NOT RUN FROM QUEUED TASKS')
        
    ####################################
    
    ###MESSAGE CODE ####################
    def add_string_message(self, message):
        self.logger.debug('add_message()')
        msg = pickleFunctions.unPickleServer(message['data'])
        self.logger.debug('RECIEVED MESSAGE: ', msg)
        
    #####################################
    
    
        
if __name__=='__main__':
    print ('starting a ClusterExecutorNode...')
    node = ClusterNode()
    node.boot('0.0.0.0', 9000)
    
    