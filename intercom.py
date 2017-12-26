#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 18:37:52 2017

@author: lukanen
"""
import requests 
import json
import pickleFunctions


def get_request(location, params={}):
    try:
        response = requests.get(location, params=params)
        return response
    except:
        return None

def post_request(location, data, headers={"Content-Type":"application/json"}):
    try:
        response = requests.post(location,data=json.dumps(data)
            ,headers=headers)
        return response
    except:
        return None

def connect_as_slave(server_ip, server_port, node):
    return post_slave_node(server_ip, server_port, node)

def post_master_node(server_ip, server_port, node):
    data = node.convert_to_dictionary()
    location = location_assembler(server_ip, server_port, "/addMasterNode")
    response = post_request(location, data)
    return parse_response(response)
    
def post_slave_node(server_ip, server_port, node):
    data = node.convert_to_dictionary()
    location = location_assembler(server_ip, server_port, "/addSlaveNode")
    response = post_request(location, data)
    return parse_response(response)
    
def close_server(server_ip, server_port):
    location = location_assembler(server_ip, server_port, "/shutdown")
    response = requests.get(location) 
    return response


##############################
##############################
##############################
    
def post_string_message(server_ip, server_port, message, params={}):
    message_data = message.createDictionary()
    message_data.update(params)
    location = location_assembler(server_ip, server_port, "/addStringMessage")
    response = post_request(location, message_data)
    return parse_response(response)

def post_task(server_ip, server_port, task, params={}):
    task_data = task.createDictionary()
    task_data.update(params)
    location = location_assembler(server_ip, server_port, "/addTask")
    response = post_request(location, task_data)
    return parse_response(response)

def get_counts(server_ip, server_port, params={}):
    location = location_assembler(server_ip, server_port, "/counts")
    response = get_request(location)
    return parse_response(response)

def get_node_info(server_ip, server_port, params={}):
    location = location_assembler(server_ip, server_port, "/nodeInfo")
    response = get_request(location)
    return parse_response(response)

def get_task_list(server_ip, server_port, params={}):
    location = location_assembler(server_ip, server_port, "/getTaskList")
    response = get_request(location, params)
    task_list = parse_response(response)
    return pickleFunctions.unPickleListServer(task_list['data'])

def connect_user(server_ip, server_port, params={}):
    location = location_assembler(server_ip, server_port, "/connectUser")
    response = post_request(location, params)
    return parse_response(response)

#def post_node_info_by_index(server_ip, server_port):

def parse_response(response):
    if (response!=None):
        try:
            return json.loads(response.text)
        except:
            return response.text
    return None

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
                "to_peer": node.convert_to_dictionary()}
    
    def get_peer_to_peer(node):
        return {"type": Directive.type_peer_to_peer,
                "to_node":node.convert_to_dictionary()}
        
    def get_to_cluster(cluster):
        return {"type": Directive.type_to_cluster,
                "to_cluster": cluster.convert_to_dictionary()}