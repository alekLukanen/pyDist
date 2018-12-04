# -*- coding: utf-8 -*-
"""

@author: Aleksandr Lukanen
"""

import sys
sys.path.append('.')

import time
import concurrent
import logging
import sys

from pyDist import Interfaces, Nodes
from pyDist.TaskManager import TaskManager

from pyDist import exSheet


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


def ex(a, b):
    time.sleep(0.001)
    return [True, a, b]

    
def submit_test(tasks_needed):
    logger.debug('sending tasks using submit')
    
    time.sleep(1.0)
    cluster = Interfaces.ClusterExecutor('0.0.0.0', 9000)
    cluster.connect('submit_test')
    
    logger.debug('sending the task...')
    # send a message to the node
    for i in range(0,tasks_needed): # add three tasks
        _ = cluster.submit(exSheet.estimatePi, 1_000_000)

    task_count_conf = 0
    pi_est = 0.0
    for task in [f for f in cluster.as_completed()]:
        task_count_conf += 1
        pi_est += task.result()
        logger.info('\x1b[31mTASKS NEEDED: %d, TASKS RETURNED: %d, RESULT: %s\x1b[0m' %
                    (tasks_needed, task_count_conf, task))

    assert task_count_conf == tasks_needed

    logger.info(f'Estimate of pi: {pi_est/tasks_needed}')

    cluster.disconnect()
    time.sleep(1)
    logger.debug('finished the submit test')


def map_test(tasks_needed, chuncksize=1):
    logger.debug('sending tasks using map')

    time.sleep(1.0)
    cluster = Interfaces.ClusterExecutor('0.0.0.0', 9000)
    cluster.connect('map_test')

    logger.debug('mapping the tasks...')
    results = cluster.map(exSheet.estimatePi, [1_000_000 for i in range(0, tasks_needed)], chunksize=chuncksize)

    task_count_conf = 0
    pi_est = 0.0
    for result in [res for res in results]:
        task_count_conf += len(result)
        logger.info('\x1b[31mTASKS NEEDED: %d, TASKS RETURNED: %d, RESULT: %s\x1b[0m' %
                    (tasks_needed, task_count_conf, result))
        for est in result:
            pi_est += est
        #logger.info(f'result: {result}')

    assert task_count_conf == tasks_needed

    logger.info(f'Estimate of pi: {pi_est/tasks_needed}')

    cluster.disconnect()
    logger.info('finished the map test')


if __name__ == '__main__':
    logger.debug('basic ClusterExecutor.py tests')
    
    tasks_needed = 13

    start_submit_time = time.time()
    submit_test(tasks_needed)
    end_submit_time = time.time()
    submit_run_time = end_submit_time - start_submit_time

    start_map_time = time.time()
    map_test(tasks_needed, chuncksize=int(tasks_needed/6))  # break into 6 chunks
    end_map_time = time.time()
    map_run_time = end_map_time - start_map_time

    logger.debug('Ended the test...')
    logger.debug('\x1b[31m--- TEST SUMMARY ---\x1b[0m')
    logger.debug(f'\x1b[31m-* tasks_needed: {tasks_needed}\x1b[0m')
    logger.debug(f'\x1b[31m-* submit ran in: {submit_run_time}\x1b[0m')
    logger.debug(f'\x1b[31m-* map ran in: {map_run_time}\x1b[0m')


