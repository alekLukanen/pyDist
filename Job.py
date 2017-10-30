#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 15:14:10 2017

@author: alek
"""

import pickleFunctions

def convertBaseToRunner(job):
    jobRunner = JobRunner()
    jobRunner.job_from_dictionary(job.convert_to_dictionary())
    return jobRunner
    
def convertRunnerToBase(job):
    baseJob = BaseJob()
    baseJob.job_from_dictionary( job.convert_to_dictionary() )
    return baseJob()

class BaseJob(object):
    
    def __init__(self):
        self.file_name = ''                  #string
        self.num_instances = 1               #int
        self.from_ip = None                  #string
        self.from_port = None                #int
        self.data = None                     #object
        self.job_id = 'example_id'           #object
        self.function_name = 'no_function'   #string
        self.arguements = ()                 #object
        self.return_value = ''               #object
        self.finished = False                #bool
        
    def convert_root_node(self):
        if (self.root_node==None):
            return None
        else:
            return self.root_node.convert_to_dictionary()

    def convert_to_dictionary(self):
        dictionary = {
                'file_name': self.file_name,
                'num_instances': self.num_instances,
                'from_ip': self.from_ip,
                'from_port': self.from_port,
                'data': pickleFunctions.createPickle(self.data).decode('utf-8'),
                'job_id': pickleFunctions.createPickle(self.job_id).decode('utf-8'),
                'function_name': self.function_name,
                'arguements': pickleFunctions.createPickle(self.arguements).decode('utf-8'),
                'return_value': pickleFunctions.createPickle(self.return_value).decode('utf-8'),
                'finished': self.finished
                }
        return dictionary
    
    def job_from_dictionary(self, data):
        self.file_name = data['file_name'] if 'file_name' in data else ''
        self.num_instances = data['num_instances'] if 'num_instances' in data else 0
        self.from_ip = data['from_ip'] if 'from_ip' in data else None
        self.from_port = data['from_port'] if 'from_port' in data else None
        self.data = pickleFunctions.unPickle(data['data'].encode()) if 'data' in data else ''
        self.job_id = pickleFunctions.unPickle(data['job_id'].encode()) if 'job_id' in data else ''
        self.function_name = data['function_name'] if 'function_name' in data else ''
        self.arguements = pickleFunctions.unPickle(data['arguements'].encode()) if 'arguements' in data else ()
        self.return_value = pickleFunctions.unPickle(data['return_value'].encode()) if 'return_value' in data else ''
        self.finished = data['finished'] if 'finished' in data else False
     
    def __str__(self):
        return ("<job_id:%s, file_name:%s, function_name:%s, len(arguements):%d>" 
            % (self.job_id,self.file_name, self.function_name, len(self.arguements)))
        
class JobRunner(BaseJob):
    
    def __init__(self):
        BaseJob.__init__(self)
        self.node_index = -1       #int
        self.node_id = -1          #int
        self.job_manager_id = -1   #string/int
        self.processor = None      #bool
        
    def convert_to_dictionary(self):
        dictionary = {
                'file_name': self.file_name,
                'num_instances': self.num_instances,
                'node_index': self.node_index,
                'from_ip': self.from_ip,
                'from_port': self.from_port,
                'data': pickleFunctions.createPickle(self.data).decode('utf-8'),
                'job_id': pickleFunctions.createPickle(self.job_id).decode('utf-8'),
                'function_name': self.function_name,
                'arguements': pickleFunctions.createPickle(self.arguements).decode('utf-8'),
                'return_value': pickleFunctions.createPickle(self.return_value).decode('utf-8'),
                'finished': self.finished,
                'job_manager_id': self.job_manager_id,
                'processor': True if self.processor!=None else False
                }
        return dictionary
        
    def job_from_dictionary(self, data):
        self.file_name = data['file_name'] if 'file_name' in data else ''
        self.num_instances = data['num_instances'] if 'num_instances' in data else 0
        self.from_ip = data['from_ip'] if 'from_ip' in data else None
        self.from_port = data['from_port'] if 'from_port' in data else None
        self.data = pickleFunctions.unPickle(data['data'].encode()) if 'data' in data else ''
        self.job_id = pickleFunctions.unPickle(data['job_id'].encode()) if 'job_id' in data else ''
        self.function_name = data['function_name'] if 'function_name' in data else ''
        self.arguements = pickleFunctions.unPickle(data['arguements'].encode()) if 'arguements' in data else ()
        self.return_value = pickleFunctions.unPickle(data['return_value'].encode()) if 'return_value' in data else ''
        self.finished = data['finished'] if 'finished' in data else False
        self.sent_to_node = data['sent_to_node'] if 'sent_to_node' in data else -1
        self.run = data['run'] if 'run' in data else False
        self.node_index = data['node_index'] if 'node_index' in data else 0
        self.job_manager_id = data['job_manager_id'] if 'job_manager_id' in data else -1
        self.processor = None
        
        
        
        
        
        
        