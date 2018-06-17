#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 16:25:08 2017

@author: alek
"""
import sys
sys.path.append('../')

import time

from pyDist.TaskManager import TaskManager

def waitFunc(a,t):
    time.sleep(a)
    return a, t

if __name__ == '__main__':
    
    taskManager = TaskManager()
    for i in range(0,20):
        taskManager.tasks.append(
                taskManager.executor.submit(waitFunc, 0.5, i))
        
    for task in taskManager.as_completed():
        print ('wait time: %s, future: %s' % task.result())
    