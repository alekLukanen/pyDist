#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 12:27:31 2017

@author: Aleksandr Lukanen
"""

import asyncio
lp = asyncio.get_event_loop()
if lp.is_closed()==True or lp.is_running()==True:
    print ('the current eventloop was closed, a new one was created')
    lp_temp = asyncio.new_event_loop()
    asyncio.set_event_loop(lp_temp)

from aiohttp import web
import json
import logging
import sys

from pyDist import Interfaces, TaskManager, pickleFunctions, Tasks, endpoints

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
        
        #self.io_loop = asyncio.new_event_loop()
        self.server_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.server_loop)
        
        self.work_item_added = True
        
        print('server_loop: ', self.server_loop)
        
        self.app = web.Application()
        self.app.router.add_route('GET', '/', endpoints.index)
        self.app.router.add_route('GET', '/counts', endpoints.counts)
        self.app.router.add_route('GET', '/nodeInfo', endpoints.nodeInfo)
        self.app.router.add_route('GET', '/getFinishedTaskList', endpoints.getFinishedTaskList)
        self.app.router.add_route('GET', '/getSingleTask', endpoints.getSingleTask)
        self.app.router.add_route('POST', '/addTask', endpoints.addTask)
        self.app.router.add_route('POST', '/addStringMessage', endpoints.addStringMessage)
        self.app.router.add_route('POST', '/connectUser', endpoints.connectUser)
        
        print('server_loop: ', self.server_loop)
        
    ###USER INTERACTION CODE##############
    async def shutdown_executor(self):
        self.taskManager.executor.shutdown(wait=False)

    ######################################
        
    ###NODE INFO CODE ####################    
    def get_counts(self):
        num_cores = self.taskManager.num_cores
        num_tasks_in_running_list = len(self.taskManager.tasks)
        num_tasks_in_queue_list = len(self.taskManager.queued_tasks)
        dictionary = {'num_tasks_running': num_tasks_in_running_list
                      , 'num_tasks_queue': num_tasks_in_queue_list
                      , 'num_cores':num_cores}
        return json.dumps(dictionary)
    
    def get_info(self):
        return json.dumps(self.interface.info())
    
    def get_tasks_finished(self, params):
        user = self.interfaces.find_user_by_user_id(params['user_id'])
        if (user!=None):
            dictionary = {'data': pickleFunctions.pickleListServer(user.tasks_finished)}
            return json.dumps(dictionary)
        else:
            return json.dumps({'data': [], 'error': 'no user for that user_id'})
        
    async def get_a_finished_work_item(self, params):
        if 'user_id' not in params:
            await asyncio.sleep(1)
            return json.dumps({'data': None, 'error': 'a user_id was not provided'})

        user = self.interfaces.find_user_by_user_id(params['user_id'])
        if user!=None:
            await self.interfaces.wait_for_first_finished_work_item_for_user(user)
            work_item = self.interfaces.find_finished_work_item_for_user(user)
            self.interfaces.reset_finished_event_for_user(user)
            if work_item!=None:
                dictionary = {'data': work_item.pickle()}
                return json.dumps(dictionary)
            else:
                self.logger.warning('the work item was of Nonetype')
                return json.dumps({'data': None, 'error': 'work item was none'})
        else:
            return json.dumps({'data': None, 'error': 'no user for that user_id'})
        
    ###################################

    def boot(self, ip, port):
        endpoints.node = self #give the endpoints a reference to this object
        self.interface.ip = ip
        self.interface.port = port
        print('app: ', self.app)
        print('server_loop: ', self.server_loop)
        web.run_app(self.app, host=self.interface.ip, port=self.interface.port)
        
    def get_address(self):
        return "http://%s:%d" % (self.interface.ip, self.interface.port)
    
    ###TASK CODE ######################
    def sign_work_item(self, work_item):
        work_item.cluster_trace.append(self.interface.get_signature())
    
    def add_existing_work_item_async(self, task):
        self.logger.debug('adding_existing_work_item_async()')
        work_item = pickleFunctions.unPickleServer(task['data'])
        
        #always pickle inner task data here
        work_item.pickleInnerData()
        
        #add the task to the users submitted tasks array
        user = self.interfaces.find_user_by_user_id(task['user_id'])
        if (user!=None):
            work_item.interface_id = user.interface_id
            user.work_items_recieved.append(work_item)
        else:
            self.logger.warning('THE USER DOES NOT EXIST, TASK NOT ADDED')
            self.work_item_added = False
            return
        
        if len(self.taskManager.tasks) < self.taskManager.num_cores:
            future_for_work_item = self.taskManager.executor.submit(Tasks.caller_helper, work_item)
            future_for_work_item.add_done_callback(self.work_item_finished_callback)
            self.taskManager.tasks.append(future_for_work_item)
            self.logger.debug('work_item (running): %s' % work_item)
        else:
            self.taskManager.queued_tasks.append(work_item)
            self.logger.debug('work_item (queued): %s' % work_item)
        self.work_item_added = True
        return
    
    def run_task_from_user(self):
        if len(self.taskManager.tasks) < self.taskManager.num_cores:
            user, work_item = self.interfaces.find_user_work_item()
            if user == work_item == None:
                self.logger.debug('No users have tasks to perfom')
                return False
            future = self.taskManager.executor.submit(Tasks.caller_helper, work_item)
            future.add_done_callback(self.work_item_finished_callback)
            self.taskManager.submit(future)
            user.work_items_running.append(work_item.item_id)
            self.logger.debug('added work item to running list')
            return True
        else:
            self.logger.debug('work item was not run because cores are available')
            return False
        
    def add_work_item_to_user(self, data):
        self.logger.debug('adding_existing_task_async()')
        work_item = pickleFunctions.unPickleServer(data['data'])
        self.sign_work_item(work_item)
        
        #always pickle inner task data here
        work_item.pickleInnerData()
        
        #add the task to the users submitted tasks array
        user = self.interfaces.find_user_by_user_id(data['user_id'])
        if (user!=None):
            work_item.interface_id = user.interface_id
            user.work_items_received.append(work_item)
            self.logger.debug('work_item (added to user receive list): %s' % work_item)
        else:
            self.logger.warning('THE USER DOES NOT EXIST, TASK NOT ADDED')
            self.work_item_added = False
            return
        #set add bool and find user task to run
        self.work_item_added = True
        self.run_task_from_user()
    
    def add_existing_task(self, task):
        self.logger.debug('add_existing_task()')
        #self.server_loop.call_soon_threadsafe(self.add_existing_task_async, task)
        self.server_loop.call_soon_threadsafe(self.add_work_item_to_user, task)
        return json.dumps({'task_added': self.work_item_added})
    
    def work_item_finished_callback(self, future):
        self.logger.debug('task_finished_callback() result: %s' % future)
        #get the work item from future and unpickle the inside of the work item
        work_item = future.result()
        work_item.unpickleInnerData()

        #here is where the taskmanager is udated based on the 
        #tasks finished callback.
        #subract one from the taskmanagers couter
        #add a done result to the task
        #update the task in user_tasks with the result
        #remove the future from the task list, this keeps the futures list small
        t_updated = self.interfaces.update_work_item_in_user(work_item) #self.taskManager.update_task_by_id(returned_task)
        t_removed = self.taskManager.remove_work_item_from_task_list_by_id(work_item)
        t_added   = self.run_task_from_user()
        #show warning messages when necessary
        self.logger.debug('user.counts(): %s' 
                % self.interfaces.find_user_by_interface_id(work_item.interface_id).counts())
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
    
    