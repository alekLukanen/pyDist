#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 17:41:51 2017

@author: lukanen
"""

import signal
import psutil
import pyDist.endpointSetup as endpointSetup


def create_master_node(ip, port):
    node = endpointSetup.setup_cluster_node()
    node.boot('0.0.0.0', 9000)


def kill_child_processes(parent_pid, sig=signal.SIGTERM):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for process in children:
        process.send_signal(sig)


def print_break():
    print()
    print('--------------------')
    print()


def wait_for_user():
    print('waiting for your input')
    var = input('type something') 

