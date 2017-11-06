#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 16:25:08 2017

@author: alek
"""

import time
import concurrent.futures

def waitFunc(a,t):
    time.sleep(a)
    return a, t

executor = concurrent.futures.ProcessPoolExecutor(max_workers=4)
tasks = []

for i in range(0,100):
    tasks.append(executor.submit(waitFunc, 0.01, i))

for future in concurrent.futures.as_completed(tasks):
    print ('wait time: %s, future: %s' % future.result())

