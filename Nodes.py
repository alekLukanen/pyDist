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

import NodeInterface
import endpoints
import Tasks

import pickleFunctions    

class ClusterNode(object):
    
    def __init__(self):
        self.interface = NodeInterface.NodeInterface()
        self.server_interfaces = []
        self.client_interfaces = []
        
        self.tasks = []
        
        self.node_id_tick = 0
        self.job_id_tick = 0
        
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
        num_tasks = len(self.tasks)
        dictionary = {'num_tasks': num_tasks, 'num_cores':num_cores}
        return json.dumps( dictionary )
    
    def get_task_list(self):
        dictionary = {'data': pickleFunctions.pickleListServer(self.tasks)}
        return json.dumps( dictionary )
    ###################################
        
    def boot(self, ip, port):
        endpoints.node = self #give the endpoints a reference to this object
        self.interface.ip = ip
        self.interface.port = port
        web.run_app(self.app, host=self.interface.ip, port=self.interface.port)
        
    def increment_id_tick(self):
        self.node_id_tick+=1
        
    def increment_job_id_tick(self):
        self.job_id_tick+=1
        
    def get_address(self):
        return "http://%s:%d" % (self.interface.ip, self.interface.port)
    
    ###TASK CODE ######################
    def sign_task(self, task_object):
        task_object.cluster_trace.append(self.interface.get_signature())
    
    def add_existing_task_async(self, task_object):
        print ('adding_existing_task_async()')
        self.sign_task(task_object)
        self.tasks.append(task_object)
    
    def add_existing_task(self, task):
        print ('add_existing_task')
        task_object = pickleFunctions.unPickleServer(task['data'])
        future = self.server_loop.call_soon_threadsafe(self.add_existing_task_async, task_object)
        print (future)
        return True
    ####################################
    
    ###MESSAGE CODE ####################
    def add_string_message(self, message):
        print ('add_message')
        msg = pickleFunctions.unPickleServer(message['data'])
        print ('RECIEVED MESSAGE: ', msg)
        
    #####################################
    
    #EXECUTOR METHODS HERE####################
    
    #submit a new job here
    #this is where a new task needs to be created
    def submit(self, fn, *args, **kwards):
        task = Tasks.Task()
        
        print ('submit')
        
    def map(self, func, *iterables, timeout=None, chuncksize=1):
        print ('map function')
        
    def shutdown(self, wait=True):
        print ('shutdown()')
        self.server_loop.call_soon_threadsafe(self.server_loop.stop)
    
    ##########################################
    
    
        
if __name__=='__main__':
    print ('starting a ClusterExecutorNode...')
    node = ClusterNode()
    node.boot('0.0.0.0', 9000)
    
    