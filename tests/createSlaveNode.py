#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 19:34:21 2018

@author: alek
"""

import sys
sys.path.append('.')

print ('starting a ClusterExecutorNode...')
import pyDist.endpointSetup

node = pyDist.endpointSetup.setup_cluster_node()
node.boot('0.0.0.0', 9000)
