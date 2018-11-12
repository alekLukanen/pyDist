

import sys
import time
import concurrent.futures
import asyncio
import os

from pyDist import Nodes, intercom
from pyDist.TaskManager import TaskManager
from tests.testerHelpers import kill_child_processes

#sys.path.append('.')  # add calling directory to the path


def create_master_node(ip, port):
    node = Nodes.ClusterNode()
    node.boot(ip, port)


def create_slave_node(ip, port, connection_ip, connection_port):
    node = Nodes.ClusterNode()
    node.interface.ip = ip
    node.interface.port = port

    print('connecting to node(s)...')
    node.connect_to_node(connection_ip, connection_port)

    node.boot(ip, port)


def test_unary_star():
    print('unary star structure test')

    taskManager = TaskManager()
    taskManager.num_cores = 2
    taskManager.executor = concurrent.futures.ProcessPoolExecutor(taskManager.num_cores)

    taskManager.tasks.append(
        taskManager.executor.submit(create_master_node, '0.0.0.0', 9000)
    )

    time.sleep(0.5)

    taskManager.tasks.append(
        taskManager.executor.submit(create_slave_node, '0.0.0.0', 9001, '0.0.0.0', 9000)
    )

    io_loop = asyncio.get_event_loop()
    counts_from_9000 = io_loop.run_until_complete(intercom.get_node_info('0.0.0.0', 9000))
    counts_from_9001 = io_loop.run_until_complete(intercom.get_node_info('0.0.0.0', 9001))
    print('counts_from_9000: ', counts_from_9000)
    print('counts_from_9001: ', counts_from_9001)

    # shutdown the executor then kill all child processes
    taskManager.executor.shutdown(wait=False)
    kill_child_processes(os.getpid())

    assert True

def test_binary_star():
    print('binary star structure test')


def test_trinary_star():
    print('trinary star structure test')


if __name__ == '__main__':
    test_unary_star()
