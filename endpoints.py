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
    print ('/')
    return web.Response(text='Hello Aiohttp!')

async def addJob(request):
    print ('/addJob')
    task_data = json.loads( request.text() )
    node.add_existing_task(task_data)
    return web.Response(text='got the job')

async def nodeCounts(request):
    print ('/nodeCounts')
    data = node.get_counts()
    return data

