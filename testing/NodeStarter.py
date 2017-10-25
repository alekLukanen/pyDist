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

node = Node()
node.boot('0.0.0.0',9001) #need to wait 1 second for the flask app to boot...
node.connect('0.0.0.0',9000)


node2 = Node()
node2.boot('0.0.0.0',9002) #need to wait 1 second for the flask app to boot...
node2.connect('0.0.0.0',9000)


