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

def add_jobs_to_node(node):
    job = BaseJob()
    job.file_name = "exSheet"
    job.function_name = "estimatePi"
    job.arguements = (100000,)
    job.num_instances = 1
    for _ in range(0,5):
        node.add_job(job)
    '''
    count = 0
    while(True):
        result = node.get_result()
        print ('(%d) value of pi: %s' %  (count, result.return_value))
        count+=1
    '''

if __name__ == '__main__':
    node = start_head_node()
    testerHelpers.wait_for_user()
    add_jobs_to_node(node)
    