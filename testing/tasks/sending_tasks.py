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
    
def ex(a,b):
    time.sleep(0.01)
    return [True,a,b]
    
def send_tasks(tasks_needed):
    logger.debug('sending messages (PROCESS 2)')
    
    time.sleep(1.5)
    cluster = Interfaces.ClusterExecutor('0.0.0.0', 9000)
    cluster.connect('testing_user')
    
    params={'user_id': 'testing_user'}
    
    logger.debug('sending the task...')
    #send a message to the node
    for i in range(0,tasks_needed): #add three tasks
        t1 = Tasks.Task()
        t1.fn = ex
        t1.args = (i,2)
        t1.id = 'task_%d' % i
        added = cluster.add_task(t1)
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
        if (task.pickled_inner()): task.unpickleInnerData()
        #logger.debug('task.result: %s' % task.result())
        if (task.done()):
            task_count_conf += 1
        
    logger.info('\x1b[31mTASKS NEEDED: %d, TASKS RETURNED: %d, SUCCESS: %s\x1b[0m' % 
                (tasks_needed, task_count_conf, (tasks_needed==task_count_conf)))
    
    time.sleep(1)
    logger.debug('end of test')

if __name__ == '__main__':
    logger.debug('basic task sending test')
    
    tasks_needed = 3
    taskManager.tasks.append(
                taskManager.executor.submit(send_tasks,tasks_needed))
    try:
        node = start_node()
    except Exception as e:
        #logger.debug('node.taskManager.tasks: %s' % node.taskManager.tasks)
        #logger.debug('node.taskManager.tasks[0].result().result(): %s' % node.taskManager.tasks[0].result().result())
        logger.debug('Ened the test...')
