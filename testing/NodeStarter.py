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

def start_single_node(server_ip='0.0.0.0', server_port=9000
                      , client_ip='0.0.0.0', client_port=9001):
    
    node = Node()
    #need to wait 1 second for the flask app to boot...
    node.boot(client_ip,client_port)
    node.connect(server_ip,server_port)
    return node

#connect two nodes to the server at 9000
def start_two_nodes(server_ip='0.0.0.0'
                    , server_port=9000, client_ip='0.0.0.0'):
    
    node = start_single_node('0.0.0.0', 9000, '0.0.0.0', 9001)
    node2 = start_single_node('0.0.0.0', 9000, '0.0.0.0', 9002)
    return node, node2

if __name__ == '__main__':
    #start_two_nodes()
    node = start_single_node()