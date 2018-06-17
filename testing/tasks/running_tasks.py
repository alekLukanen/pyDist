#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 22:03:23 2017

@author: alek
"""
import sys
sys.path.append('../../')

from pyDist import Nodes
import logging
import sys

from pyDist.TaskManager import TaskManager

#change these up for use in other cases
taskManager = TaskManager()
#taskManager.executor = concurrent.futures.ThreadPoolExecutor(4)

#logging utility
logging.basicConfig(format='%(filename)-20s:%(lineno)-43s | %(levelname)-8s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()


def run_this(i):
    logger.debug('run_this() was called at index %d' % i)
    return True

def callback(a):
    logger.debug('callback(%s)' % a)

def start_node():
    logger.debug('starting the node (PROCESS MAIN)')
    node = Nodes.ClusterNode()
    for i in range(0,3):
        task = node.taskManager.executor.submit(run_this,i)
        task.add_done_callback(node.work_item_finished_callback)
        node.taskManager.submit(task)
    #node.start_updating()
    #node.boot('0.0.0.0', 9000)
    #logger.debug('node stopped')
    return node

if __name__ == '__main__':
    logger.debug('basic task running test')
    
    node = start_node()
    
