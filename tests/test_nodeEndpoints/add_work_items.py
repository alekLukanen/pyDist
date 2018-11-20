
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

from pyDist.TaskManager import TaskManager
import tests.testerHelpers as testHelpers

#logging utility
logging.getLogger("Nodes").setLevel(logging.WARNING)
logging.getLogger("endpoints").setLevel(logging.WARNING)
logging.basicConfig(format='%(name)-12s:%(lineno)-3s | %(levelname)-8s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def connect_n_users_and_send_c_work_items(n, c):
    cluster_exs = []
    for i in range(0, n):
        cluster_ex = Interfaces.ClusterExecutor('0.0.0.0', 9000)
        cluster_ex.connect(f'connect_one_user({i})', group_id='connect_users')
        cluster_exs.append(cluster_ex)

    for cluster_ex in cluster_exs:
        for j in range(0, c):
            _ = cluster_ex.submit(exSheet.estimatePi, 100_000)

    time.sleep(0.5)
    for j in range(0, n):
        io_loop = asyncio.get_event_loop()
        counts = io_loop.run_until_complete(intercom.get_user_counts('0.0.0.0', 9000,
                                                                    params={'user_id': f'connect_one_user({j})'}))

        logger.debug(f'counts: {counts}')

    interface_stats = json.loads(urllib.request.urlopen("http://0.0.0.0:9000/interfaceStats").read())
    logger.debug(f'interface_stats: {interface_stats}')
    assert interface_stats['data']['num_users'] == n
    assert interface_stats['data']['num_nodes'] == 0
    assert interface_stats['data']['num_clients'] == 0

    for cluster_ex in cluster_exs:
        task_count_conf = 0
        pi_est = 0.0
        for task in [f for f in cluster_ex.as_completed()]:
            task_count_conf += 1
            pi_est += task.result()
            logger.debug('\x1b[31mTASKS NEEDED: %d, TASKS RETURNED: %d, RESULT: %s\x1b[0m' %
                        (c, task_count_conf, task))

        assert task_count_conf == c

    time.sleep(1)
    for cluster_ex in cluster_exs:
        cluster_ex.disconnect()


def start_one_node_and_connect_n_users_and_send_c_work_items(n,c):
    task_manager = TaskManager()
    task_manager.num_cores = 2
    task_manager.executor = concurrent.futures.ProcessPoolExecutor(task_manager.num_cores)

    #task_manager.tasks.append(
    #    task_manager.executor.submit(testHelpers.create_master_node, '0.0.0.0', 9000)
    #)

    logger.debug('----- creating executor and sending tasks -----')
    connect_n_users_and_send_c_work_items(n, c)

    # shutdown the executor then kill all child processes
    logger.debug('Shutting down the test processes')
    task_manager.executor.shutdown(wait=False)
    testHelpers.kill_child_processes(os.getpid())


def test_start_one_node_and_connect_one_user():
    start_one_node_and_connect_n_users_and_send_c_work_items(1, 15)


if __name__=='__main__':
    test_start_one_node_and_connect_one_user()
