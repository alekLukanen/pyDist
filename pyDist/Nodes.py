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
import aiohttp_jinja2
import jinja2
import json
import logging
import sys
import os

import signal
import psutil

from pyDist import Interfaces, TaskManager,\
    pickleFunctions, Tasks, endpointSetup, intercom, WorkItemOptimizer
import pyDist.comms

logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)


class ClusterNodeV2(pyDist.comms.ClusterExecutor.Comm,
                    pyDist.comms.WorkItems.Comm,
                    pyDist.comms.NodeToNode.Comm):

    def __init__(self, num_cores):
        self.interface = Interfaces.NodeInterface()
        self.interfaces = Interfaces.InterfaceHolder()
        self.work_item_optimizer = WorkItemOptimizer.WorkItemOptimizer(self.interfaces, num_cores)

        self.io_loop = asyncio.new_event_loop()
        self.server_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.server_loop)
        self.app = web.Application()

        pyDist.comms.ClusterExecutor.Comm.__init__(self)
        pyDist.comms.WorkItems.Comm.__init__(self)
        pyDist.comms.NodeToNode.Comm.__init__(self)

    def set_ip_and_port(self, ip, port):
        self.interface.ip = ip
        self.interface.port = port

    def boot(self, ip, port):
        self.interface.ip = ip
        self.interface.port = port
        web.run_app(self.app, host=self.interface.ip, port=self.interface.port)

    def get_address(self):
        return "http://%s:%d" % (self.interface.ip, self.interface.port)

    # NODE-TO-NODE COMMS###############
    def connect_to_node(self, ip, port):
        print('connect_to_node...')
        self.logger.debug('CONNECTING NODE TO (ip: %s, port: %s)' % (ip, port))
        self.logger.debug('self.io_loop: %s' % self.io_loop)
        response = None
        try:
            response = self.io_loop.run_until_complete(intercom.connect_node(ip,
                        port, params={
                        'node_id': str(self.interface.node_id),
                        'ip': self.interface.ip,
                        'port': self.interface.port}))
        except Exception as e:
            print('exception: ', e)

        print('response: ', response)
        if 'connected' in response and response['connected']:
            print('connected!')

    ###################################

    # USER INTERACTION CODE##############
    async def shutdown_executor(self):
        self.logger.debug(f'called shutdown executor')
        self.work_item_optimizer.task_manager.executor.shutdown(wait=False)
        try:
            parent = psutil.Process(os.getpid())
        except psutil.NoSuchProcess:
            return
        children = parent.children(recursive=True)
        for process in children:
            process.send_signal(signal.SIGTERM)

    ######################################
