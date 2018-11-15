#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 18:37:52 2017

@author: Aleksandr Lukanen
"""
from pyDist import pickleFunctions

import aiohttp


async def get_request(location, params={}):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(location, params=params) as response:
                return response
        except aiohttp.client_exceptions.ClientConnectorError:
            return None


async def post_request(location, data, headers={"Content-Type":"application/json"}):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(location, json=data, headers=headers) as response:
                return response
        except aiohttp.client_exceptions.ClientConnectorError:
            return None


async def get_json_request(location, params={}):
    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(location, params=params) as response:
                    return await response.json()
            except aiohttp.client_exceptions.ClientConnectorError:
                return {}
    except ValueError:
        return {}


async def post_json_request(location, data, headers={"Content-Type":"application/json"}):
    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(location, json=data, headers=headers) as response:
                    return await response.json()
            except aiohttp.client_exceptions.ClientConnectorError:
                return {}
    except ValueError:
        return {}

##############################
##############################
##############################


async def post_string_message(server_ip, server_port, message, params={}):
    message_data = message.createDictionary()
    message_data.update(params)
    location = location_assembler(server_ip, server_port, "/addStringMessage")
    response = await post_json_request(location, message_data)
    return response


async def post_work_item(server_ip, server_port, task, params={}):
    task_data = task.createDictionary()
    task_data.update(params)
    location = location_assembler(server_ip, server_port, "/addWorkItem")
    response = await post_json_request(location, task_data)
    return response


async def get_counts(server_ip, server_port, params={}):
    location = location_assembler(server_ip, server_port, "/counts")
    response = await get_json_request(location)
    return response


async def get_node_info(server_ip, server_port, params={}):
    location = location_assembler(server_ip, server_port, "/nodeInfo")
    response = await get_json_request(location)
    return response


async def get_finished_task_list(server_ip, server_port, params={}):
    location = location_assembler(server_ip, server_port, "/getFinishedTaskList")
    response = await get_json_request(location, params)
    return pickleFunctions.unPickleListServer(response['data'])


async def get_single_task(server_ip, server_port, params={}):
    location = location_assembler(server_ip, server_port, "/getSingleTask")
    response = await get_json_request(location, params)
    return pickleFunctions.unPickleServer(response['data'])


async def get_interface_holder_interfaces(server_ip, server_port, params={}):
    location = location_assembler(server_ip, server_port, "/getInterfaceHolderInterfaces")
    response = await get_json_request(location, params)
    return response['data']


async def connect_user(server_ip, server_port, params={}):
    location = location_assembler(server_ip, server_port, "/connectUser")
    response = await post_json_request(location, params)
    return response


async def connect_node(node_ip, node_port, params={}):
    print('connect_node using intercom')
    location = location_assembler(node_ip, node_port, "/connectNode")
    response = await post_json_request(location, params)
    return response


def location_assembler(ip, port, endpoint):
    address = "http://%s:%d" % (ip, port)
    location = "%s%s" % (address, endpoint)
    return location


class Directive:
    type_global = "global"
    type_peer_to_peer = "peer_to_peer"
    type_to_cluster = "to_cluster"
    
    def get_global(node):
        return {"type":Directive.type_global,
                "to_peer": node.info()}
    
    def get_peer_to_peer(node):
        return {"type": Directive.type_peer_to_peer,
                "to_node":node.info()}
        
    def get_to_cluster(cluster):
        return {"type": Directive.type_to_cluster,
                "to_cluster": cluster.info()}