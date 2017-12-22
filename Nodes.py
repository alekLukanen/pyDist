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
import Message

import pickleFunctions    

class ClusterNode(object):
    
    def __init__(self):
        self.interface = NodeInterface.NodeInterface()
        self.server_interfaces = []
        self.client_interfaces = []
        
        self.tasks = []
        
        self.ip = '0.0.0.0'
        self.port = 9000
        
        self.node_id_tick = 0
        self.job_id_tick = 0
        
        self.server_loop = asyncio.get_event_loop()
        self.io_loop = asyncio.new_event_loop()
        
        self.app = web.Application(loop=self.server_loop)
        self.app.router.add_route('GET', '/', endpoints.index)
        self.app.router.add_route('POST', '/addJob', endpoints.addJob)
        self.app.router.add_route('POST', '/addStringMessage', endpoints.addStringMessage)
        
        self.handler = None
        self.server = None
        self.serverFuture = None
        
    def get_node_counts(self):
        num_cores = self.interface.num_cores
        num_running = len(self.node_ref.jobManager.running_job_dictionary)
        dictionary = {'num_cores':num_cores, 'num_running': num_running
                      , 'num_queued': self.job_queue_count}
        return json.dumps( dictionary )
        
    def boot(self, ip, port):
        endpoints.node = self #give the endpoints a reference to this object
        #self.handler = self.app.make_handler()
        #self.server = self.server_loop.create_server(self.handler, self.ip, self.port)
        #self.io_loop.run_in_executor(None, self.startRESTEndpoints)
        web.run_app(self.app, host=self.ip, port=self.port)
        
    def startRESTEndpoints(self):
        print ('start rest endpoints')
        print ('server: ', self.server)
        self.serverFuture = self.server_loop.run_until_complete(self.server)
        try:
            print ('...in try')
            self.server_loop.run_forever()
        finally:
            print ('1...')
            self.server.close()
            print ('2...')
            #self.loop.run_until_complete(self.server.wait_closed())
            print ('3...')
            self.io_loop.run_until_complete(self.app.shutdown())
            print ('4...')
            self.io_loop.run_until_complete(self.handler.shutdown(60.0))
            print ('5...')
            self.io_loop.run_until_complete(self.app.cleanup())
        self.server_loop.close()
        self.io_loop.stop()
        print ('the rest endpoints have been shutdown')
        
    def increment_id_tick(self):
        self.node_id_tick+=1
        
    def increment_job_id_tick(self):
        self.job_id_tick+=1
        
    def get_address(self):
        return "http://%s:%d" % (self.ip, self.port)
    
    async def add_existing_task_async(self, task_data):
        task_object = Tasks.Task()
        task_object.create_from_dictionary(task_data)
        self.tasks.append(task_object)
    
    def add_existing_task(self, task):
        print ('add_existing_task')
        future = asyncio.run_coroutine_threadsafe(self.add_existing_task_async(task), self.loop)
        future.result()
        return True
    
    def add_string_message(self, message):
        print ('add_message')
        msg = pickleFunctions.unPickleServer(message['data'])
        print ('RECIEVED MESSAGE: ', msg)
    
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
    node = ClusterNode()
    node.boot('0.0.0.0', 9000)
    
    