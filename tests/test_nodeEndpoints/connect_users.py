#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 19:30:06 2017

@author: lukanen
"""

import sys
sys.path.append('.')

from pyDist import Interfaces, intercom
import concurrent
import logging
import urllib.request
import json
import os
import time
import asyncio

from pyDist.TaskManager import TaskManager
import tests.testerHelpers as testHelpers

#logging utility
logging.getLogger("Nodes").setLevel(logging.WARNING)
logging.getLogger("endpoints").setLevel(logging.WARNING)
logging.basicConfig(format='%(name)-12s:%(lineno)-3s | %(levelname)-8s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def connect_n_users(n):
    cluster_exs = []
    for i in range(0, n):
        cluster_ex = Interfaces.ClusterExecutor('0.0.0.0', 9000)
        cluster_ex.connect(f'connect_one_user({i})', group_id='connect_users')
        cluster_exs.append(cluster_ex)
        #cluster_ex.disconnect()

    time.sleep(0.5)
    interface_stats = json.loads(urllib.request.urlopen("http://0.0.0.0:9000/interfaceStats").read())
    logger.debug(f'interface_stats: {interface_stats}')
    assert interface_stats['data']['num_users'] == n
    assert interface_stats['data']['num_nodes'] == 0
    assert interface_stats['data']['num_clients'] == 0

    for cluster_ex in cluster_exs:
        cluster_ex.disconnect()


def start_one_node_and_connect_n_users(n):
    task_manager = TaskManager()
    task_manager.num_cores = 2
    task_manager.executor = concurrent.futures.ProcessPoolExecutor(task_manager.num_cores)

    task_manager.tasks.append(
        task_manager.executor.submit(testHelpers.create_master_node, '0.0.0.0', 9000)
    )

    logger.debug('----- creating executor and connecting users -----')
    connect_n_users(n)

    io_loop = asyncio.get_event_loop()
    counts = io_loop.run_until_complete(intercom.get_user_counts('0.0.0.0', 9000,
                                                                 params={'user_id': 'connect_one_user(0)'}))

    logger.debug(f'counts: {counts}')

    # shutdown the executor then kill all child processes
    logger.debug('Shutting down the test processes')
    task_manager.executor.shutdown(wait=False)
    testHelpers.kill_child_processes(os.getpid())


def test_start_one_node_and_connect_one_user():
    start_one_node_and_connect_n_users(1)


def test_start_one_node_and_connect_two_users():
    start_one_node_and_connect_n_users(2)


def test_start_one_node_and_connect_three_users():
    start_one_node_and_connect_n_users(3)


def test_start_one_node_and_connect_a_bunch_of_users():
    start_one_node_and_connect_n_users(64)


if __name__ == '__main__':
    logger.debug('basic task sending test')
    
    test_start_one_node_and_connect_one_user()
    #test_start_one_node_and_connect_a_bunch_of_users()
