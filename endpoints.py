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

logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.basicConfig(format='%(filename)-20s:%(lineno)-3s | %(levelname)-8s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()

node = None

async def index(request):
    logger.debug('/')
    return web.Response(text='Hello Aiohttp!')

async def addTask(request):
    logger.debug('/addTask')
    task_data = json.loads( await request.text() )
    added = node.add_existing_task(task_data)
    if (added == True):
        return web.Response(text='True')
    else:
        return web.Response(text='False')

async def addStringMessage(request):
    logger.debug('/addStringMessage')
    message_data = json.loads( await request.text() )
    node.add_string_message(message_data)
    return web.Response(text='got the message')

async def counts(request):
    logger.debug('/counts')
    data = node.get_counts()
    return web.Response(body=data)

async def getTaskList(request):
    logger.debug('/getTaskList')
    return web.Response(body=node.get_task_list())
