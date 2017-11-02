#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 16:03:08 2017

@author: alek
"""

import json
import requests
import logging

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("flask").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)

def get_request(location):
    try:
        response = requests.get(location)
        return response
    except:
        return None

def post_request(location, data, headers={"Content-Type":"application/json"}):
    try:
        response = requests.post(location,data=json.dumps(data)
            ,headers=headers)
        return response
    except:
        return None
    
def location_assembler(ip, port, endpoint):
    address = "http://%s:%d" % (ip, port)
    location = "%s%s" % (address, endpoint)
    return location

def parse_response(response):
    if (response!=None):
        try:
            return json.loads(response.text)
        except:
            return response.text
    return None

class NodeInterface(object):
    
    def __init__(self):
        self.ip = None
        self.port = None
        self.num_cores = None
        self.num_running = None
        self.num_queued = None
        self.jobs_sent = []
        
    def update_variables(self):
        location = location_assembler(self.ip, self.port, "/nodeCounts")
        response = get_request(location)
        response = parse_response(response)
        self.num_cores = response["num_cores"] if "num_cores" in response else 1
        self.num_running = response["num_running"] if "num_running" in response else 1
        self.num_queued = response["num_queued"] if "num_queued" in response else 1
        
    def add_job(self, job):
        job_data = job.convert_to_dictionary()
        location = location_assembler(self.ip, self.port, "/addJob")
        response = post_request(location, job_data)
        if (parse_response(response)=='job added'):
            self.jobs_sent.append(job)
            return True
        else:
            return False
    
    def get_num_cores(self):
        return self.num_cores
    
    def get_num_running(self):
        return self.num_running
    
    def convert_to_dictionary(self):
        dictionary = {
                'ip': self.ip,
                'port': self.port,
                'num_cores': self.num_cores,
                'num_queued': self.num_queued
                }
        return dictionary
    
    def create_from_dictionary(self, dictionary):
        self.ip = dictionary['ip'] if 'ip' in dictionary else None
        self.port = dictionary['port'] if 'port' in dictionary else None
        self.num_cores = dictionary['num_cores'] if 'num_cores' in dictionary else None
        self.num_queued = dictionary['num_queued'] if 'num_queued' in dictionary else None
    
    def NodeInterface_from_dictionary(self, data):
        self.ip = data["ip"] if 'ip' in data else '0.0.0.0'
        self.port = data["port"] if 'port' in data else 9000
    
    
        