#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 16:03:08 2017

@author: alek
"""

import json
import uuid
import logging
import sys
import threading
import asyncio
import concurrent
from concurrent.futures import _base
from concurrent.futures import process
from functools import partial

from pyDist import intercom, Tasks


class InterfaceHolder(object):
    
    def __init__(self):
        logging.basicConfig(format='%(name)-12s:%(lineno)-3s | %(levelname)-8s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        self.user_interfaces = {}
        self.node_interfaces = {}
        self.client_interfaces = []  # I think this is for the webpage stuff???
        
        self._condition = threading.Condition()

    def get_interfaces_as_dict(self):
        interface_dict = {'user_interfaces': [],
                'node_interfaces': []}

        for key in self.user_interfaces:
            interface_dict['user_interfaces'].append(str(self.user_interfaces[key]))

        for key2 in self.node_interfaces:
            interface_dict['node_interfaces'].append(self.node_interfaces[key2].info())

        return interface_dict

    def connect_node(self, node_data):
        with self._condition:
            self.logger.debug('connecting node: %s' % node_data)
            node_interface = self.find_node_by_node_id(node_data['node_id'])
            if node_interface == None:
                node_interface = NodeInterface()
                node_interface.node_id = node_data['node_id']
                node_interface.ip = node_data['ip']
                node_interface.port = node_data['port']
                self.node_interfaces.update({str(node_interface.node_id): node_interface})
                self.logger.debug('node_interfaces (UPDATED): %s' % self.node_interfaces)
                return json.dumps({'connected': True})
            else:
                return json.dumps({'connected': True})

    def find_node_by_node_id(self, node_id):
        return self.node_interfaces[node_id] if node_id in self.node_interfaces else None

    ##TODO:
    # need to make the execution of the node stats such as
    # core count async so this execution go faster. It will
    # be a sequential query for now because that will be
    # easier for tests.
    def update_node_interface_data(self):
        """
        For each node in the list of node interfaces update
        the data for that node (Ex: core count, available cores, etc).
        :return: None
        """
        for node_interface in self.node_interfaces:
            node_interface.update_counts()  # updates: num cores, num running, num queued

    def connect_user(self, user_data):
        with self._condition:
            self.logger.debug('connecting user: %s' % user_data)
            user_interface = self.find_user_by_user_id(user_data['user_id'])
            if user_interface == None:
                user_interface = UserInterface(user_data['user_id'], user_data['group_id'])
                self.user_interfaces.update({user_interface.user_id: user_interface})
                return json.dumps({'connected': True})
            else:
                return json.dumps({'connected': True})
        
    def find_user_by_user_id(self, user_id):
        return self.user_interfaces[user_id] if user_id in self.user_interfaces else None
        
    def find_user_work_item(self):
        for user_id in self.user_interfaces:
            user = self.user_interfaces[user_id]
            if len(user.work_items_received)>0:
                work_item = user.work_items_received.pop()
                return user, work_item
        return None, None
    
    def update_work_item_in_user(self, work_item, ):
        with self._condition:
            for user_id in self.user_interfaces:
                user = self.user_interfaces[user_id]
                if user.interface_id == work_item.interface_id:
                    user.work_items_running.remove(work_item.item_id)
                    user.finished_work_item(work_item)
                    self.logger.debug(f'job finished event: {user.finished_event}')
                    self.remove_work_item_in_user_by_item_id(user, work_item.item_id)
                    return True
            return False
    
    def find_user_by_interface_id(self, interface_id):
        for user_id in self.user_interfaces:
            user = self.user_interfaces[user_id]
            if user.interface_id == interface_id:
                return user
        return None
    
    def remove_work_item_in_user_by_item_id(self, user, item_id):
        with self._condition:
            for work_item in user.work_items_received:
                if work_item.item_id == item_id:
                    user.work_items_received.remove(work_item)
                    
    def wait_for_first_finished_work_item_for_user(self, user):
        user._finished_event.wait()
        
    def find_finished_work_item_for_user(self, user):
        for work_item in user.work_items_finished:
            if work_item.ran:
                user.work_items_finished.remove(work_item)
                return work_item
        return None
    
    def reset_finished_event_for_user(self, user):
        user.reset_finished_event()
        
    def __str__(self):
        return ('#users: %d, #servers: %d, #clients: %d' 
                % (len(self.user_interfaces)
                , len(self.node_interfaces)
                , len(self.client_interfaces)))

class UserInterface(object):
    
    def __init__(self, user_id, group_id):
        self.interface_id = uuid.uuid4()
        self.user_id = user_id
        self.group_id = group_id

        self.work_items_received = []
        self.work_items_running = []
        self.work_items_finished = []
        
        self._condition = threading.Condition()
        self._finished_event = threading.Event()
        
    def finished_work_item(self, work_item):
        with self._condition:
            self.work_items_finished.append(work_item)
            self._finished_event.set()
        
    def reset_finished_event(self):
        with self._condition:
            if (len(self.work_items_finished)==0):
                self._finished_event.clear()
            else:
                self._finished_event.set()
       
    def counts(self):
        return ('#recv: %d, #running: %d, #fin: %d'
                % (len(self.work_items_received)
                , len(self.work_items_running)
                , len(self.work_items_finished)))
        
    def __str__(self): 
        return ('user_id: %s, group_id: %s' 
               % (self.user_id, self.group_id))
    

class NodeInterface(object):
    
    def __init__(self):
        self.node_id = uuid.uuid4()
        self.ip = None
        self.port = None
        self.num_cores = None
        self.num_running = None            #for user side only
        self.num_queued = None             #for user side only
        self.tasks_sent = {}               #for user side only
        self.params = {}

        self.event_loop = asyncio.get_event_loop()

        logging.basicConfig(format='%(name)-12s:%(lineno)-3s | %(levelname)-8s | %(message)s'
                            , stream=sys.stdout, level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
    def info(self):
        return {'node_id': str(self.node_id), 'ip': self.ip
                , 'port': self.port, 'num_cores': self.num_cores
                , 'num_running': self.num_running
                , 'num_queued': self.num_queued
                , 'params': self.params}
        
    def get_signature(self):
        return {'node_id': self.node_id, 'ip': self.ip
                , 'port': self.port}

    def update_counts(self):
        response = self.event_loop.run_until_complete(intercom.get_counts(self.ip, self.port))
        self.num_cores = response["num_cores"] if "num_cores" in response else 1
        self.num_running = response["num_tasks_running"] if "num_tasks_running" in response else 1
        self.num_queued = response["num_tasks_queued"] if "num_tasks_queued" in response else 1
        return response

    def update_info(self):
        response = self.event_loop.run_until_complete(intercom.get_node_info(self.ip, self.port))
        self.node_id = uuid.UUID(str(response['node_id'])) if 'node_id' in response else None
        self.ip = response['ip'] if 'ip' in response else None
        self.port = response['port'] if 'port' in response else None
        self.num_cores = response['num_cores'] if 'num_cores' in response else None
        self.num_running = response['num_running'] if 'num_running' in response else None
        self.num_queued = response['num_queued'] if 'num_queued' in response else None
        return response
    
    def add_task(self, task):
        self.logger.debug('C <--- U task: %s' % task)
        response = self.event_loop.run_until_complete(intercom.post_work_item(self.ip, self.port
                                                                              , task, params=self.params))
        if (response['task_added']==True):
            self.tasks_sent[task.task_id] = task
            return True
        else:
            return False
    
    def get_num_cores(self):
        return self.num_cores
    
    def get_num_running(self):
        return self.num_running


class ClusterExecutor(_base.Executor):
    
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.user_id = None
        self.group_id = None
        self.params = {}

        self.tasks_sent = {}
        self.tasks_pending = {}
        self.futures = []

        self.tasks_received = 0

        self.worker_loop = None
        self.event_loop = asyncio.get_event_loop()
        self.worker_thread = None

        self._condition = threading.Condition()
        self._work_item_sent = threading.Event()
        self._closed = threading.Event()

        logging.basicConfig(format='%(name)-12s:%(lineno)-3s | %(levelname)-8s | %(message)s'
                            , stream=sys.stdout, level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
    def connect(self, user_id, group_id='base'):
        response = self.event_loop.run_until_complete(intercom.connect_user(self.ip
                                                                            , self.port, params={'user_id': user_id, 'group_id': group_id}))

        if 'connected' in response and response['connected']:
            self.user_id = user_id
            self.group_id = group_id
            self._update_params()

            self.worker_loop = asyncio.new_event_loop()
            self.worker_thread = threading.Thread(target=self.event_loop_worker, args=(self.worker_loop,))
            self.worker_thread.start()
            return True
        else:
            return False

    def disconnect(self):
        self._closed.set()
        self._work_item_sent.set()

        self.worker_loop.call_soon_threadsafe(self.stop_worker_loop)
        self.worker_thread.join()

        self.worker_loop.stop()
        self.worker_loop.close()

        self.logger.debug(f'self.worker_thread: {self.worker_thread}')
        self.logger.debug(f'self.worker_loop: {self.worker_loop}')
        self.logger.debug(f'self.event_loop : {self.event_loop }')

    def stop_worker_loop(self):
        self.logger.debug('*----> called stop worker loop')
        self.worker_loop.stop()

    def _update_params(self):
        self.params = {'user_id': self.user_id
                    , 'group_id': self.group_id}
        
    #EXECUTOR METHODS HERE####################
    
    #submit a new job here
    #this is where a new task needs to be created
    def submit(self, fn, *args, **kwargs):
        task = Tasks.Task(fn, args, kwargs)
        with self._condition:
            task_added = self.add_work_item(task)
            if task_added:
                self._work_item_sent.set()
        return task.future
        
    def map(self, fn, *iterables, timeout=None, chunksize=1):
        self.logger.debug('map function')
        if chunksize < 1:
            raise ValueError("chunksize must be >= 1.")

        results = super().map(partial(process._process_chunk, fn),
                              process._get_chunks(*iterables, chunksize=chunksize),
                              timeout=timeout)
        return results

    def as_completed(self):
        return concurrent.futures.as_completed(self.futures)
        
    def shutdown(self, wait=True):
        self.logger.debug('shutdown()')
        #self.server_loop.call_soon_threadsafe(self.server_loop.stop)
    
    ##########################################

    def add_work_item(self, task):
        self.logger.debug('C <--- U work item: %s' % task)
        response = self.event_loop.run_until_complete(intercom.post_work_item(self.ip,
                                                                              self.port,
                                                                              task,
                                                                              params=self.params))
        if 'task_added' in response and response['task_added']:
            with self._condition:
                self.tasks_sent[task.work_item.item_id] = task
                self.add_future(task.future)
            return True
        else:
            with self._condition:
                self.logger.debug('task added to pending tasks')
                self.tasks_pending[task.work_item.item_id] = task
                self.add_future(task.future)
            return False

    def add_future(self, future):
        self.futures.append(future)

    async def finished_work_item_thread(self):
        self.logger.debug('*** Started the finished_task_thread')
        while True:
            try:
                self._work_item_sent.wait()
                with self._condition:
                    self.logger.debug(f'*** self.tasks_received={self.tasks_received} ***')
                    if self.tasks_received == len(self.tasks_sent):
                        if self._closed.is_set():
                            break
                        self._work_item_sent.clear()
                self._work_item_sent.wait()

                if self._closed.is_set():
                    break
                work_item = await intercom.get_single_task(self.ip, self.port, params=self.params)
            except RuntimeError as e:
                self.logger.error('Error in finished work item process')
                if self._closed.is_set():
                    break
            self.logger.debug('C ---> U task: %s' % work_item)
            if work_item.item_id in self.tasks_sent:
                with self._condition:
                    self.tasks_sent[work_item.item_id].update(work_item)
                    self.tasks_received += 1
        self.logger.debug('*** Ended the finished_task_thread')

    def event_loop_worker(self, loop):
        self.logger.debug('*** start of loop worker')
        asyncio.set_event_loop(loop)
        #asyncio.run_until_complete(self.finished_work_item_thread())
        try:
            #loop.run_forever()
            loop.run_until_complete(self.finished_work_item_thread())
        except RuntimeError as e:
            self.logger.error('*** stopped updating work items (should be here)')
        finally:
            self.logger.debug('*** finally shutting down async gens ***')
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        self.logger.debug('*** end of loop worker')
        exit()
        
    def __str__(self):
        return ('ip: %s, port: %s, user_id: %s, group_id: %s' 
                % (self.ip, self.port, self.user_id, self.group_id))


if __name__ == '__main__':
    print('Interfaces Testing')
