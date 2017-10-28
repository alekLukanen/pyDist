#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 17:40:36 2017

@author: lukanen
"""
import sys
sys.path.append('../')

from Node import Node
from Job import BaseJob
import time
import testerHelpers

def start_head_node(server_ip='0.0.0.0', server_port=9000):
    node = Node()
    node.boot(server_ip,server_port)
    return node

def check_interfaces(node):
    for interface in node.interfaces:
        print ('jobs sent to interface (ip:%s , port%d): %s' 
               % (interface.ip, interface.port, [str(job) for job in interface.jobs_sent]))

def add_jobs_to_node(node, count):
    job = BaseJob()
    job.file_name = "exSheet"
    job.function_name = "estimatePi"
    job.arguements = (1000000,)
    job.num_instances = 1
    for _ in range(0,count):
        node.add_job(job)
    
    total = 0
    total_value = 0.0
    while(True):
        result = node.get_result()
        total_value+=result.return_value
        print ('(%d) value of pi: %s' %  (total, result.return_value))
        if (total==count-1):
            break
        total+=1
        
    print ('(ANSWER) average value of PI: %1.5f' % (total_value/count))
    

if __name__ == '__main__':
    node = start_head_node(server_ip='192.168.0.15', server_port=9000)
    testerHelpers.wait_for_user()
    add_jobs_to_node(node, 50)
    node.request_close_server()
    
