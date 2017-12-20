#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 22:31:33 2017

@author: lukanen
"""
import sys
sys.path.append('../../')

import Nodes
import time
import intercom
import Message

if __name__ == '__main__':
    print ('basic message test')
    node = Nodes.ClusterExecutorNode()
    node.boot('0.0.0.0', 9000)
    print ('started node...')
    
    time.sleep(1.5)
    print ('message sent...')
    #send a message to the node
    intercom.post_string_message('0.0.0.0', 9000, Message.StringMessage('hello, world1!'))
    intercom.post_string_message('0.0.0.0', 9000, Message.StringMessage('hello, world2!'))
    intercom.post_string_message('0.0.0.0', 9000, Message.StringMessage('hello, world3!'))
    
    time.sleep(1)
    node.shutdown()    
    print ('end of test')