

import sys
import time
sys.path.append('../../')

import concurrent.futures


from pyDist import Nodes
from pyDist.TaskManager import TaskManager

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

if __name__ == '__main__':
    print('star structure test')

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
