#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 16:43:16 2017

@author: alek
"""

from aiohttp import web
import json

node = None

async def index(request):
    print ('- /')
    return web.Response(text='Hello Aiohttp!')

async def addTask(request):
    print ('- /addTask')
    task_data = json.loads( await request.text() )
    added = node.add_existing_task(task_data)
    if (added == True):
        return web.Response(text='True')
    else:
        return web.Response(text='False')

async def addStringMessage(request):
    print ('- /addStringMessage')
    message_data = json.loads( await request.text() )
    node.add_string_message(message_data)
    return web.Response(text='got the message')

async def counts(request):
    print ('- /counts')
    data = node.get_counts()
    return web.Response(body=data)

async def getTaskList(request):
    print ('- /getTaskList')
    return web.Response(body=node.get_task_list())
