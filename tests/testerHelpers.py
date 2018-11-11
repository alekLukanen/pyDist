#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 17:41:51 2017

@author: lukanen
"""

import sys
sys.path.append('../')

import time
import requests

def shut_down_server(address):
    print ('shutting down the server...')
    location = "%s/shutdown" % address
    response = requests.get(location)
    print (response.text)
    
def print_break():
    print ()
    print ('--------------------')
    print ()
    
def wait_for_user():
    print ('waiting for your input')
    var = input('type something') 
    