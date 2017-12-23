# -*- coding: utf-8 -*-
"""

@author: lukanen
"""

import sys
sys.path.append('../../')

import Nodes
import time
import intercom
import Tasks
import concurrent
import logging
import sys

from TaskManager import TaskManager

#change these up for use in other cases
taskManager = TaskManager()
taskManager.executor = concurrent.futures.ThreadPoolExecutor(4)

logging.basicConfig(format='%(filename)-20s:%(lineno)-43s | %(levelname)-8s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()
#'%(asctime)s | %(name)-20s | %(levelname)-10s | %(message)s'

def start_node():
    logger.debug('starting the node (PROCESS MAIN)')
    node = Nodes.ClusterNode()
    node.boot('0.0.0.0', 9000)
    logger.debug('node stopped')
    
def send_tasks():
    logger.debug('sending messages (PROCESS 2)')
    
    time.sleep(1.5)
    logger.debug('sending the task...')
    #send a message to the node
    for i in range(0,3): #add three tasks
        t1 = Tasks.Task()
        t1.task_id = 'task_%d' % i
        intercom.post_task('0.0.0.0', 9000, t1)
        logger.debug('sent a task...')
    
    logger.debug('====Wait for Counts====')
    time.sleep(1)
    counts = intercom.get_counts('0.0.0.0', 9000)
    logger.debug('counts: %s' % counts)
    
    tasks = intercom.get_task_list('0.0.0.0', 9000)
    logger.debug('====Tasks====')
    for task in tasks:
        logger.debug('task: %s' % task)
    
    time.sleep(1)   
    logger.debug('end of test')

if __name__ == '__main__':
    logger.debug('basic message test')
    
    taskManager.tasks.append(
                taskManager.executor.submit(send_tasks,))
    try:
        start_node()
    except KeyboardInterrupt:
        logger.debug('Ened the test...')
