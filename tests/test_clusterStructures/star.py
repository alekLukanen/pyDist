

import sys
import time
import concurrent.futures
import asyncio
import os
import logging
import subprocess

sys.path.append('.')  # add calling directory to the path

from pyDist import Nodes, intercom, Interfaces, exSheet, endpointSetup
from pyDist.TaskManager import TaskManager
from tests.testerHelpers import kill_child_processes
from tests import prettyPrinter as pp

#logging utility
logging.getLogger("Nodes").setLevel(logging.WARNING)
logging.getLogger("endpoints").setLevel(logging.WARNING)
logging.basicConfig(format='%(name)-12s:%(lineno)-3s | %(levelname)-8s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def popen_node(ip, port, connections):
    command = ['python', 'tests/spawn.py', ip, str(port)]
    for connection in connections:
        command.append(connection[0])
        command.append(str(connection[1]))
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL)
    logger.debug(f'process -> {process}')


def create_master_node(ip, port):
    node = endpointSetup.setup_cluster_node()
    node.boot(ip, port)


def create_slave_node(ip, port, connection_ip, connection_port):
    node = endpointSetup.setup_cluster_node()
    node.set_ip_and_port(ip, port)
    node.connect_to_node(connection_ip, connection_port)
    node.boot(ip, port)


def create_Nary_star(N, send_tasks=False):
    task_manager = TaskManager()
    task_manager.num_cores = N+2
    task_manager.executor = concurrent.futures.ProcessPoolExecutor(task_manager.num_cores)

    task_manager.tasks.append(
        task_manager.executor.submit(create_master_node, '0.0.0.0', 9000)
    )

    time.sleep(1.0)

    for i in range(0, N):
        task_manager.tasks.append(
            task_manager.executor.submit(create_slave_node, '0.0.0.0', 9001+i, '0.0.0.0', 9000)
        )

    io_loop = asyncio.get_event_loop()

    time.sleep(2.0)  # have to wait for the node connection to register on the master/server node

    interfaces_from_9000 = io_loop.run_until_complete(intercom.get_interface_holder_interfaces('0.0.0.0', 9000))
    #interfaces_from_9001 = io_loop.run_until_complete(intercom.get_interface_holder_interfaces('0.0.0.0', 9001))

    logger.debug('----- interfaces on master node -----')
    pp.print_list('* ', interfaces_from_9000['node_interfaces'])
    #print('----- interfaces_from_9001 -----')
    #pp.print_list('* ', interfaces_from_9001['node_interfaces'])

    logger.debug(f'os.getpid(): {os.getpid()}')

    if send_tasks:
        logger.debug('----- creating executor and sending tasks -----')
        cluster_ex = Interfaces.ClusterExecutor('0.0.0.0', 9000)
        cluster_ex.connect(f'create_Nary_star({N})', group_id='star_tests')
        send_tasks_to_node(cluster_ex)
        cluster_ex.disconnect()

    logger.debug(f'os.getpid(): {os.getpid()}')

    # shutdown the executor then kill all child processes
    logger.debug('Shutting down the test processes')
    task_manager.executor.shutdown(wait=False)
    kill_child_processes(os.getpid())

    assert len(interfaces_from_9000['node_interfaces']) == N


#def test_unary_star_with_tasks():
#    logger.debug('unary star structure test with tasks')
#    create_Nary_star(1, send_tasks=True)


def test_unary_star():
    logger.debug('unary star structure test')
    create_Nary_star(1)
    #create_Nary_star(1, send_tasks=True)


def test_binary_star():
    logger.debug('binary star structure test')
    create_Nary_star(2)


def test_trinary_star():
    logger.debug('trinary star structure test')
    create_Nary_star(3)


def test_ridiculous_star():
    logger.debug('ridiculous star structure test')
    create_Nary_star(10)


def send_tasks_to_node(cluster_ex):
    logger.debug('send_test_tasks_to_node()')

    tasks_needed = 20

    logger.debug('sending the task...')
    # send a message to the node
    for i in range(0, tasks_needed):  # add three tasks
        _ = cluster_ex.submit(exSheet.estimatePi, 1_000_000)

    task_count_conf = 0
    pi_est = 0.0
    for task in [f for f in cluster_ex.as_completed()]:
        task_count_conf += 1
        pi_est += task.result()
        logger.info('\x1b[31mTASKS NEEDED: %d, TASKS RETURNED: %d, RESULT: %s\x1b[0m' %
                    (tasks_needed, task_count_conf, task))

    assert task_count_conf == tasks_needed

    logger.info(f'Estimate of pi: {pi_est/tasks_needed}')

    logger.debug('finished the submit test')


if __name__ == '__main__':
    #test_unary_star()
    popen_node('0.0.0.0', 9000, [('0.0.0.0', 9001), ('0.0.0.0', 9002)])
    kill_child_processes(os.getpid())
    logger.debug(f'--- end of main file ---')
