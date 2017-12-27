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

import Interfaces
from TaskManager import TaskManager

#change these up for use in other cases
taskManager = TaskManager()
taskManager.executor = concurrent.futures.ThreadPoolExecutor(4)

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
    
def ex(a,b):
    time.sleep(0.01)
    return [True,a,b]
    
def send_tasks(tasks_needed):
    logger.debug('sending messages (PROCESS 2)')
    
    time.sleep(1.5)
    cluster = Interfaces.ClusterExecutor('0.0.0.0', 9000)
    cluster.connect('testing_user')
    
    logger.debug('sending the task...')
    #send a message to the node
    for i in range(0,tasks_needed): #add three tasks
        added = cluster.submit(ex, i,2)
        logger.debug('task added: %s' % added)
        
    logger.debug('sent %d tasks' % tasks_needed)
    logger.debug('====Wait for Counts====')
    time.sleep(1)
    counts = cluster.update_counts()
    logger.debug('counts: %s' % counts)
    
    tasks = cluster.get_finished_task_list()
    logger.debug('====Tasks====')
    task_count_conf = 0
    for task in tasks:
        logger.debug('task: %s' % task)
        task.unpickleInnerData()
        task.new_condition()
        #logger.debug('task.result: %s' % task.result())
        if (task.done()):
            task_count_conf += 1
            
    gen = concurrent.futures.as_completed(tasks)
    logger.debug("tasks[0]._waiters: %s" % tasks[0]._waiters)
    for task_sub in gen:
        logger.debug('task_sub: %s' % task_sub)
        
    logger.info('\x1b[31mTASKS NEEDED: %d, TASKS RETURNED: %d, SUCCESS: %s\x1b[0m' % 
                (tasks_needed, task_count_conf, (tasks_needed==task_count_conf)))
    
    time.sleep(1)
    logger.debug('end of test')

if __name__ == '__main__':
    logger.debug('basic task sending test')
    
    tasks_needed = 3
    
    send_tasks(tasks_needed)
    #node = start_node()
    
    '''
    taskManager.tasks.append(
                taskManager.executor.submit(send_tasks,tasks_needed))
    try:
        node = start_node()
    except Exception as e:
        #logger.debug('node.taskManager.tasks: %s' % node.taskManager.tasks)
        #logger.debug('node.taskManager.tasks[0].result().result(): %s' % node.taskManager.tasks[0].result().result())
        logger.debug('Ened the test...')
        '''