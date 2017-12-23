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

from TaskManager import TaskManager

def start_node():
    print ('starting the node (PROCESS MAIN)')
    node = Nodes.ClusterNode()
    node.boot('0.0.0.0', 9000)
    print ('started node...')
    
def send_tasks():
    print ('sending messages (PROCESS 2)')
    
    time.sleep(1.5)
    print ('sending the task...')
    #send a message to the node
    t1 = Tasks.Task()
    t1.task_id = 'task_1'
    intercom.post_task('0.0.0.0', 9000, t1)
    print ('sent the task...')
    
    time.sleep(1)
    counts = intercom.get_node_counts('0.0.0.0', 9000)
    print ('counts: ', counts)
    
    time.sleep(1)   
    print ('end of test')
    exit()

if __name__ == '__main__':
    print ('basic message test')
    
    taskManager = TaskManager()
    taskManager.tasks.append(
                taskManager.executor.submit(send_tasks,))
    
    start_node()
