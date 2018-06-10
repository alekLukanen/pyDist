#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 17:40:36 2017

@author: lukanen
"""
import sys
sys.path.append('../')

from Node import Node
import time

def start_single_node(server_ip, server_port):
    
    node = Node()
    #need to wait 1 second for the flask app to boot...
    node.boot(server_ip,server_port)
    time.sleep(1)
    return node

#connect two nodes to the server at 9000
def start_two_nodes(server_ip, server_port):
    
    node1 = start_single_node('0.0.0.0', 9001)
    node1.connect(server_ip, server_port)
    
    node2 = start_single_node('0.0.0.0', 9002)
    node2.connect(server_ip, server_port)
    
    return node1, node2

if __name__ == '__main__':
    #one node
    node = start_single_node('0.0.0.0', 9000)

    node1, node2 = start_two_nodes('0.0.0.0', 9000)