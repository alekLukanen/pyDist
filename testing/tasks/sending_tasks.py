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
taskManager.executor = concurrent.futures.ThreadPoolExecutor(1)


#logging utility
logging.basicConfig(format='%(filename)-20s:%(lineno)-43s | %(levelname)-8s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()


def start_node():
    logger.debug('starting the node (PROCESS MAIN)')
    node = Nodes.ClusterNode()
    node.boot('0.0.0.0', 9000)
    logger.debug('node stopped')
    return node
    
def ex(a,b):
    return True,a,b
    
def send_tasks():
    logger.debug('sending messages (PROCESS 2)')
    
    time.sleep(1.5)
    logger.debug('sending the task...')
    #send a message to the node
    for i in range(0,3): #add three tasks
        t1 = Tasks.Task()
        t1.fn = ex
        t1.args = (1,2)
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
        logger.debug('task.result: %s' % task.result())
    
    time.sleep(1)
    logger.debug('end of test')

if __name__ == '__main__':
    logger.debug('basic task sending test')
    
    taskManager.tasks.append(
                taskManager.executor.submit(send_tasks,))
    try:
        node = start_node()
    except Exception as e:
        logger.debug('node.taskManager.tasks: %s' % node.taskManager.tasks)
        logger.debug('node.taskManager.tasks[0].result().result(): %s' % node.taskManager.tasks[0].result().result())
        logger.debug('Ened the test...')
