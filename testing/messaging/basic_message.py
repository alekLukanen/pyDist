#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 22:31:33 2017

@author: lukanen
"""
import sys
sys.path.append('../../')

import time
from pyDist import intercom, Message, Nodes

from pyDist.TaskManager import TaskManager

def start_node():
    print('starting the node (PROCESS MAIN)')
    node = Nodes.ClusterNode()
    node.boot('0.0.0.0', 9000)
    print('started node...')
    
def send_messages():
    print ('sending messages (PROCESS 2)')
    
    time.sleep(1.5)
    #send a message to the node
    intercom.post_string_message('0.0.0.0', 9000, Message.StringMessage('hello, world1!'))
    intercom.post_string_message('0.0.0.0', 9000, Message.StringMessage('hello, world2!'))
    intercom.post_string_message('0.0.0.0', 9000, Message.StringMessage('hello, world3!'))
    
    time.sleep(1)   
    print('end of test')
    exit()

if __name__ == '__main__':
    print('basic message test')
    
    taskManager = TaskManager()
    taskManager.tasks.append(
                taskManager.executor.submit(send_messages,))
    
    start_node()
