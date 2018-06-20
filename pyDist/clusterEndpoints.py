#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 16:43:16 2017

@author: Aleksandr Lukanen
"""

from aiohttp import web
import aiohttp_jinja2
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

async def add_task(request):
    logger.debug('/addTask')
    request_data = json.loads(await request.text())
    data = node.add_existing_task(request_data)
    return web.Response(body=data, headers={"Content-Type":"application/json"})

async def add_string_message(request):
    logger.debug('/addStringMessage')
    message_data = json.loads( await request.text() )
    node.add_string_message(message_data)
    return web.Response(text='got the message')

async def counts(request):
    logger.debug('/counts')
    data = node.get_counts()
    return web.Response(body=data, headers={"Content-Type":"application/json"})

async def node_info(request):
    logger.debug('/nodeInfo')
    data = node.get_info()
    return web.Response(body=data, headers={"Content-Type":"application/json"})

async def get_finished_task_list(request):
    logger.debug('/getFinishedTaskList')
    params = request.rel_url.query
    tasks_finished = node.get_tasks_finished(params)
    return web.Response(body=tasks_finished, headers={"Content-Type":"application/json"})

async def connect_user(request):
    logger.debug('/connectUser')
    connection_data = json.loads(await request.text())
    response_data = node.interfaces.connect_user(connection_data)
    return web.Response(body=response_data, headers={"Content-Type":"application/json"})

async def get_single_task(request):
    logger.debug('/getSingleTask')
    params = request.rel_url.query
    task = await node.get_a_finished_work_item(params)
    return web.Response(body=task, headers={"Content-Type":"application/json"})

