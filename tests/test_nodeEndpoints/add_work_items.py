
import sys
sys.path.append('.')

from pyDist import Interfaces, intercom, exSheet
import concurrent
import logging
import urllib.request
import json
import os
import time
import asyncio
import subprocess

from pyDist.TaskManager import TaskManager
import tests.testerHelpers as testHelpers

#logging utility
logging.getLogger("Nodes").setLevel(logging.WARNING)
logging.getLogger("endpoints").setLevel(logging.WARNING)
logging.basicConfig(format='%(name)-12s:%(lineno)-3s | %(levelname)-8s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# the number of samples used to compute pi in the tests;
# this just changes how long the tests will take
# to complete.
SAMPLES = 100


def submit_helper(n, c, ip='0.0.0.0', port=9000):
    time.sleep(1)
    logger.debug(f'called connect_n_users_and_send_c_work_items({n}, {c})')
    cluster_exs = []
    for i in range(0, n):
        cluster_ex = Interfaces.ClusterExecutor(ip, port)
        cluster_ex.connect(f'connect_one_user({i})', group_id='connect_users')
        cluster_exs.append(cluster_ex)

    for cluster_ex in cluster_exs:
        for j in range(0, c):
            _ = cluster_ex.submit(exSheet.estimatePi, SAMPLES)

    for j in range(0, n):
        io_loop = asyncio.new_event_loop()
        counts = io_loop.run_until_complete(intercom.get_user_counts(ip, port,
                                params={'user_id': f'connect_one_user({j})'}))
        logger.debug(f'counts: {counts}')

    check_num_stats(n, ip=ip, port=port)

    for cluster_ex in cluster_exs:
        task_count_conf = 0
        pi_est = 0.0
        futures_list = []
        for f in cluster_ex.as_completed():
            futures_list.append(f)

        for task in futures_list:
            task_count_conf += 1
            pi_est += task.result()
            logger.debug('\x1b[31mTASKS NEEDED: %d, TASKS RETURNED: %d, RESULT: %s\x1b[0m' %
                        (c, task_count_conf, task))

        if task_count_conf != 0:
            logger.debug(f'\x1b[31mEstimate of pi: {pi_est/task_count_conf}\x1b[0m')

        assert task_count_conf == c

    time.sleep(1)
    for cluster_ex in cluster_exs:
        cluster_ex.disconnect()
        cluster_ex.shutdown_executor()
        time.sleep(0.5)


def mapper_helper(n, c, b, ip='0.0.0.0', port=9000):
    time.sleep(1)
    logger.debug(f'called connect_n_users_and_map_c_work_items({n}, {c})')
    cluster_exs = []
    for i in range(0, n):
        cluster_ex = Interfaces.ClusterExecutor(ip, port)
        cluster_ex.connect(f'connect_one_user({i})', group_id='connect_users')
        cluster_exs.append(cluster_ex)

    for cluster_ex in cluster_exs:
        _ = cluster_ex.map(exSheet.estimatePi, [SAMPLES for _ in range(0, c)], chunksize=b)

    for j in range(0, n):
        io_loop = asyncio.new_event_loop()
        counts = io_loop.run_until_complete(intercom.get_user_counts(ip, port,
                                params={'user_id': f'connect_one_user({j})'}))

        logger.debug(f'counts: {counts}')

    check_num_stats(n, ip=ip, port=port)

    for cluster_ex in cluster_exs:
        task_count_conf = 0
        pi_est = 0.0
        futures_list = []
        for f in cluster_ex.as_completed():
            futures_list.append(f)

        for task in futures_list:
            task_count_conf += len(task.result())
            for est in task.result():
                pi_est += est
            logger.debug('\x1b[31mTASKS NEEDED: %d, TASKS RETURNED: %d, RESULT: %s\x1b[0m' %
                        (c, task_count_conf, task.result()))

        if task_count_conf != 0:
            logger.debug(f'\x1b[31mEstimate of pi: {pi_est/task_count_conf}\x1b[0m')

        assert task_count_conf == c

    time.sleep(1)
    for cluster_ex in cluster_exs:
        cluster_ex.disconnect()
        cluster_ex.shutdown_executor()
        time.sleep(0.5)


def check_num_stats(n, ip='0.0.0.0', port=9000):
    interface_stats = json.loads(urllib.request.urlopen(f"http://{ip}:{port}/interfaceStats").read())
    logger.debug(f'interface_stats: {str(interface_stats)}')
    assert interface_stats['data']['num_users'] == n
    #assert interface_stats['data']['num_nodes'] == 0
    #assert interface_stats['data']['num_clients'] == 0


def mapper(n,c, b):
    process = subprocess.Popen(["python", "tests/spawn.py", "0.0.0.0", "9000"], stdout=subprocess.DEVNULL)
    logger.debug(f'process-> {process}')

    logger.debug('----- creating executor and sending tasks -----')
    mapper_helper(n, c, b)

    # shutdown the executor then kill all child processes
    logger.debug('Shutting down the node processes')
    testHelpers.kill_child_processes(os.getpid())


def submit(n,c):
    process = subprocess.Popen(["python", "tests/createSlaveNode.py", "0.0.0.0", "9000"], stdout=subprocess.DEVNULL)
    logger.debug(f'process-> {process}')

    logger.debug('----- creating executor and sending tasks -----')
    submit_helper(n, c)

    # shutdown the executor then kill all child processes
    logger.debug('Shutting down the node processes')
    testHelpers.kill_child_processes(os.getpid())


def test_start_one_node_and_connect_one_user_and_send_0_work_items():
    submit(1, 0)


def test_start_one_node_and_connect_one_user_and_send_1_work_items():
    submit(1, 1)


def test_start_one_node_and_connect_one_user_and_send_3_work_items():
    submit(1, 3)


def test_start_one_node_and_connect_one_user_and_send_50_work_items():
    submit(1, 50)


def test_start_one_node_and_connect_one_user_and_send_100_work_items():
    submit(1, 100)


def test_start_one_node_and_connect_one_user_and_map_12_tasks_with_chunk_size_1():
    mapper(1, 12, 1)


def test_start_one_node_and_connect_one_user_and_map_12_tasks_with_chunk_size_3():
    mapper(1, 12, 3)


def test_start_one_node_and_connect_one_user_and_map_12_tasks_with_chunk_size_6():
    mapper(1, 12, 6)


def test_start_one_node_and_connect_one_user_and_map_100_tasks_with_chunk_size_5():
    mapper(1, 100, 5)


def test_start_one_node_and_connect_one_user_and_map_100_tasks_with_chunk_size_25():
    mapper(1, 100, 25)


if __name__=='__main__':
    test_start_one_node_and_connect_one_user_and_send_100_work_items()
