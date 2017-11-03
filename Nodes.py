#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 12:27:31 2017

@author: alek
"""

import asyncio
import NodeInterface
from aiohttp import web

async def index(request):
    print ('here')
    return web.Response(text='Hello Aiohttp!')

    
class ClusterExecutorNode(object):
    
    def __init__(self):
        self.interface = NodeInterface.NodeInterface()
        self.server_interfaces = []
        self.client_interfaces = []
        
        self.ip = '0.0.0.0'
        self.port = 9000
        
        self.node_id_tick = 0
        self.job_id_tick = 0
        
        self.loop = asyncio.get_event_loop()

        self.app = web.Application(loop=self.loop)
        self.app.router.add_route('GET', '/', index)
        web.run_app(self.app, host=self.ip, port=self.port)
        
    def increment_id_tick(self):
        self.node_id_tick+=1
        
    def increment_job_id_tick(self):
        self.job_id_tick+=1
        
    def get_address(self):
        return "http://%s:%d" % (self.ip, self.port)
    
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
    
    