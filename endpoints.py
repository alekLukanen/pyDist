#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 16:43:16 2017

@author: alek
"""

from aiohttp import web
import json
import logging
import sys

logging.basicConfig(format='%(name)-12s:%(lineno)-3s | %(levelname)-8s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

node = None

async def index(request):
    logger.debug('/')
    return web.Response(text='Hello Aiohttp!')

async def addTask(request):
    logger.debug('/addTask')
    request_data = json.loads( await request.text() )
    data = node.add_existing_task(request_data)
    return web.Response(body=data)

async def addStringMessage(request):
    logger.debug('/addStringMessage')
    message_data = json.loads( await request.text() )
    node.add_string_message(message_data)
    return web.Response(text='got the message')

async def counts(request):
    logger.debug('/counts')
    data = node.get_counts()
    return web.Response(body=data)

async def nodeInfo(request):
    logger.debug('/nodeInfo')
    data = node.get_info()
    return web.Response(body=data)

async def getTaskList(request):
    logger.debug('/getTaskList')
    params = request.rel_url.query
    tasks_finished = node.get_tasks_finished(params)
    return web.Response(body=tasks_finished)

async def connectUser(request):
    logger.debug('/connectUser')
    connection_data = json.loads( await request.text() )
    response_data = node.interfaces.connect_user(connection_data)
    return web.Response(body=response_data)
