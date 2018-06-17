# -*- coding: utf-8 -*-
"""

@author: Aleksandr Lukanen
"""

import sys
sys.path.append('../../')

import time
import concurrent
import logging
import sys

from pyDist import Interfaces, Nodes
from pyDist.TaskManager import TaskManager

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
    time.sleep(0.001)
    return [True, a, b]
    
def submit_test(tasks_needed):
    logger.debug('sending tasks using submit')
    
    time.sleep(1.0)
    cluster = Interfaces.ClusterExecutor('0.0.0.0', 9000)
    cluster.connect('submit_test')
    
    logger.debug('sending the task...')
    #send a message to the node
    for i in range(0,tasks_needed): #add three tasks
        _ = cluster.submit(ex, i,2)
        
    logger.debug('sent %d tasks' % tasks_needed)

    logger.debug('====Tasks====')
    task_count_conf = 0
    for task in cluster.as_completed():
        task_count_conf += 1
        logger.info('\x1b[31mTASKS NEEDED: %d, TASKS RETURNED: %d, RESULT: %s\x1b[0m' %
                    (tasks_needed, task_count_conf, task))

    assert task_count_conf == tasks_needed

    cluster.disconnect()
    logger.debug('finished the submit test')


def map_test(tasks_needed, chuncksize=1):
    logger.debug('sending tasks using map')

    time.sleep(1.0)
    cluster = Interfaces.ClusterExecutor('0.0.0.0', 9000)
    cluster.connect('map_test')

    logger.debug('mapping the tasks...')
    results = cluster.map(ex, range(0, tasks_needed), range(tasks_needed), chunksize=chuncksize)

    task_count_conf = 0
    for result in [res for res in results]:
        task_count_conf += len(result)
        logger.info('\x1b[31mTASKS NEEDED: %d, TASKS RETURNED: %d, RESULT: %s\x1b[0m' %
                    (tasks_needed, task_count_conf, result))
        #logger.info(f'result: {result}')

    assert task_count_conf == tasks_needed

    cluster.disconnect()
    logger.info('finished the map test')


if __name__ == '__main__':
    logger.debug('basic ClusterExecutor tests')
    
    tasks_needed = 1000

    #submit_test(tasks_needed)
    map_test(tasks_needed, chuncksize=10)

    logger.debug('Ened the test...')
