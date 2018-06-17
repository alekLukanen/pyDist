#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 19:30:06 2017

@author: lukanen
"""

import sys
sys.path.append('../../')

import Nodes
import Interfaces
import time
import concurrent
import logging
import sys

from TaskManager import TaskManager

#change these up for use in other cases
taskManager = TaskManager()
taskManager.executor = concurrent.futures.ThreadPoolExecutor(1)

#logging utility
logging.getLogger("Nodes").setLevel(logging.WARNING)
logging.getLogger("endpoints").setLevel(logging.WARNING)
logging.basicConfig(format='%(name)-12s:%(lineno)-3s | %(levelname)-8s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def start_node():
    logger.debug('starting the node (PROCESS MAIN)')
    node = Nodes.ClusterNode()
    node.boot('0.0.0.0', 9000)
    logger.debug('node stopped')
    return node
    
def connect_users(users_needed):
    logger.debug('sending users (PROCESS 2)')
    time.sleep(1.5)
    
    clusters = []
    
    #send a message to the node
    for i in range(0,users_needed): #add three tasks
        cluster = Interfaces.ClusterExecutor('0.0.0.0', 9000)
        cluster.connect(('user%s' % i))
        cluster.update_counts()
        cluster.update_info()
        logger.debug('cluster: %s' % cluster)
        logger.debug('cluster.info(): %s' % cluster.info())
        clusters.append(cluster)
        
    #logger.info('\x1b[31mTASKS NEEDED: %d, TASKS RETURNED: %d, SUCCESS: %s\x1b[0m' % 
    #            (tasks_needed, task_count_conf, (tasks_needed==task_count_conf)))
    
    time.sleep(1)
    logger.debug('end of test')

if __name__ == '__main__':
    logger.debug('basic task sending test')
    
    users_needed = 1
    taskManager.tasks.append(
                taskManager.executor.submit(connect_users,users_needed))
    try:
        node = start_node()
        logger.debug('node.user_interfaces: %s' % node.user_interfaces)
    except Exception as e:
        #logger.debug('node.taskManager.tasks: %s' % node.taskManager.tasks)
        #logger.debug('node.taskManager.tasks[0].result().result(): %s' % node.taskManager.tasks[0].result().result())
        logger.debug('Ened the test...')
