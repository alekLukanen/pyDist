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

node = Node()
node.boot('0.0.0.0',9000)

#time.sleep(1)
#testerHelpers.print_break()
#input("Waiting for you")
#testerHelpers.print_break()
'''
job = JobServer()
job.file_name = "exSheet"
job.function_name = "estimatePi"
job.arguements = (10000,)
job.num_instances = 1

job.root_node = BaseJob()
for _ in range(0,16):
    node.send_job(job)

testerHelpers.node_info(node)

results = node.get_server_context().results_queue
count = 0
while(True):
    result = results.get()
    print ('(%d) value of pi: %s' %  (count, result.return_value))
    count+=1
'''