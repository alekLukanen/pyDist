

import sys
import time
import concurrent.futures
import asyncio
import os

sys.path.append('.')  # add calling directory to the path

from pyDist import Nodes, intercom
from pyDist.TaskManager import TaskManager
from tests.testerHelpers import kill_child_processes
from tests import prettyPrinter as pp


def create_master_node(ip, port):
    node = Nodes.ClusterNode()
    node.boot(ip, port)


def create_slave_node(ip, port, connection_ip, connection_port):
    node = Nodes.ClusterNode()
    node.interface.ip = ip
    node.interface.port = port

    node.connect_to_node(connection_ip, connection_port)

    node.boot(ip, port)


def create_Nary_star(N):
    task_manager = TaskManager()
    task_manager.num_cores = N+1
    task_manager.executor = concurrent.futures.ProcessPoolExecutor(task_manager.num_cores)

    task_manager.tasks.append(
        task_manager.executor.submit(create_master_node, '0.0.0.0', 9000)
    )

    time.sleep(0.5)

    for i in range(0, N):
        task_manager.tasks.append(
            task_manager.executor.submit(create_slave_node, '0.0.0.0', 9001+i, '0.0.0.0', 9000)
        )

    io_loop = asyncio.get_event_loop()

    time.sleep(1.0)  # have to wait for the node connection to register on the master/server node

    interfaces_from_9000 = io_loop.run_until_complete(intercom.get_interface_holder_interfaces('0.0.0.0', 9000))
    #interfaces_from_9001 = io_loop.run_until_complete(intercom.get_interface_holder_interfaces('0.0.0.0', 9001))

    print('----- interfaces on master node -----')
    pp.print_list('* ', interfaces_from_9000['node_interfaces'])
    #print('----- interfaces_from_9001 -----')
    #pp.print_list('* ', interfaces_from_9001['node_interfaces'])

    # shutdown the executor then kill all child processes
    task_manager.executor.shutdown(wait=False)
    kill_child_processes(os.getpid())

    assert len(interfaces_from_9000['node_interfaces']) == N


def test_unary_star():
    print('unary star structure test')
    create_Nary_star(1)


def test_binary_star():
    print('binary star structure test')
    create_Nary_star(2)


def test_trinary_star():
    print('trinary star structure test')
    create_Nary_star(3)


def test_ridiculus_star():
    print('ridiculous star structure test')
    create_Nary_star(10)


if __name__ == '__main__':
    test_unary_star()
