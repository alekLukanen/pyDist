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
import concurrent

from TaskManager import TaskManager

#change these up for use in other cases
taskManager = TaskManager()
taskManager.executor = concurrent.futures.ThreadPoolExecutor(4)

def start_node():
    print ('+ starting the node (PROCESS MAIN)')
    node = Nodes.ClusterNode()
    node.boot('0.0.0.0', 9000)
    print ('+ node stopped')
    
def send_tasks():
    print ('sending messages (PROCESS 2)')
    
    time.sleep(1.5)
    print ('sending the task...')
    #send a message to the node
    for i in range(0,3): #add three tasks
        t1 = Tasks.Task()
        t1.task_id = 'task_%d' % i
        intercom.post_task('0.0.0.0', 9000, t1)
        print ('+ sent a task...')
    
    print ('====Wait for Counts====')
    time.sleep(1)
    counts = intercom.get_counts('0.0.0.0', 9000)
    print ('+ counts: ', counts)
    
    tasks = intercom.get_task_list('0.0.0.0', 9000)
    print ('====Tasks====')
    for task in tasks:
        print ('+ task: ', task)
    
    time.sleep(1)   
    print ('+ end of test')

if __name__ == '__main__':
    print ('basic message test')
    
    taskManager.tasks.append(
                taskManager.executor.submit(send_tasks,))
    try:
        start_node()
    except KeyboardInterrupt:
        print ('Ened the test...')
