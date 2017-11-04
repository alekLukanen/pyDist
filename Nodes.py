#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 12:27:31 2017

@author: alek
"""

import asyncio
from aiohttp import web

import NodeInterface
import endpoints
import Tasks
    
class ClusterExecutorNode(object):
    
    def __init__(self):
        self.interface = NodeInterface.NodeInterface()
        self.server_interfaces = []
        self.client_interfaces = []
        
        self.tasks = []
        
        self.ip = '0.0.0.0'
        self.port = 9000
        
        self.node_id_tick = 0
        self.job_id_tick = 0
        
        self.loop = asyncio.get_event_loop()

        self.app = web.Application(loop=self.loop)
        self.app.router.add_route('GET', '/', endpoints.index)
        self.app.router.add_route('POST', '/addJob', endpoints.addJob)
        
        self.handler = None
        self.server = None
        self.serverFuture = None
        
    def boot(self, ip, port):
        endpoints.node = self #give the endpoints a reference to this object
        self.handler = self.app.make_handler()
        self.server = self.loop.create_server(self.handler, self.ip, self.port)
        self.loop.run_in_executor(None, self.startRESTEndpoints)
        
    def startRESTEndpoints(self):
        print ('start rest endpoints')
        self.serverFuture = self.loop.run_until_complete(self.server)
        self.loop.run_forever()
        print ('at end of start rest endpoints')
        
    def increment_id_tick(self):
        self.node_id_tick+=1
        
    def increment_job_id_tick(self):
        self.job_id_tick+=1
        
    def get_address(self):
        return "http://%s:%d" % (self.ip, self.port)
    
    async def add_existing_task_async(self, task):
        task_object = Tasks.Task()
        task_object.create_from_dictionary(task)
        self.tasks.append(task_object)
    
    def add_existing_task(self, task):
        print ('add_existing_task')
        future = asyncio.run_coroutine_threadsafe(self.add_existing_task_async(task), self.loop)
        future.result()
        return True
    
    #EXECUTOR METHODS HERE####################
    
    #submit a new job here
    #this is where a new task needs to be created
    def submit(self, fn, *args, **kwards):
        task = Tasks.Task()
        
        print ('submit')
        
    def map(self, func, *iterables, timeout=None, chuncksize=1):
        print ('map function')
        
    def shutdown(self, wait=True):
        self.loop.stop()
        self.loop.close()
    
    ##########################################
    
    
    def convert_to_dictionary(self):
        dictionary = {
                'interface': self.interface.convert_to_dictionary(),
                'server_interfaces': [sInt.convert_to_dictionary() for sInt in self.server_interfaces],
                'client_interfaces': [cInt.convert_to_dictionary() for cInt in self.client_interfaces],
                'node_id_tick': self.node_id_tick,
                'job_id_tick': self.job_id_tick
                }
        return dictionary
        
    def create_from_dictionary(self, dictionary):
        if ('interface' in dictionary):
            self.interface = NodeInterface.NodeInterface()
            self.interface.create_from_dictionary(dictionary['interface'])
        else:
            self.interface = None
        
        
        
if __name__=='__main__':
    print ('starting a ClusterExecutorNode...')
    node = ClusterExecutorNode()
    node.boot('0.0.0.0', 9000)
    node.add_existing_task({'a':1})
    print (node.get_address())
    
    