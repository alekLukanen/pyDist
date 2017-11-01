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

import pandas

def start_head_node(server_ip='0.0.0.0', server_port=9000):
    node = Node()
    node.boot(server_ip,server_port)
    return node

def check_interfaces(node):
    for interface in node.interfaces:
        print ('jobs sent to interface (ip:%s , port%d): %s' 
               % (interface.ip, interface.port, [str(job) for job in interface.jobs_sent]))

def add_jobs_to_node(node, count, n):
    job = BaseJob()
    job.file_name = "exSheet"
    job.function_name = "estimatePi"
    job.arguements = (n,)
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
    
    
class object_for_job(object):
    def __init__(self, n):
        self.n = n
            
#add jobs to the node that have arguements that are not python primatives.
#So place objects in the arguements, this should not hang when the job
#is sent to the client.
def add_jobs_with_object_arguements_to_node(node, count, n):
    table = pandas.DataFrame(index=range(0,count), columns=['n'])
    table['n'] = n
    job = BaseJob()
    job.file_name = "exSheet"
    job.function_name = "call_ep"
    job.num_instances = 1
    for i in range(0,count):
        job.arguements = (table.iloc[i],)
        node.add_job(job)
    
    get_results_and_check_count(node, count)
    
#for the given node check to make sure the count returned is correct
def get_results_and_check_count(node, count):
    total = 0
    while(True):
        result = node.get_result()
        print ('(%d) return_value: %s' %  (total, result.return_value))
        if (total==count-1):
            break
        total+=1
        
    print ('(COUNT) %d' % count)

if __name__ == '__main__':
    node = start_head_node(server_ip='0.0.0.0', server_port=9002)
    testerHelpers.wait_for_user()
    add_jobs_with_object_arguements_to_node(node, 16, 100)
    node.request_close_server()
    
