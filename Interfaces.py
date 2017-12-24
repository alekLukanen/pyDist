#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 16:03:08 2017

@author: alek
"""

import json
import uuid

import intercom

class UserInterface(object):
    
    def __init__(self, user_id, group_id):
        self.user_id = user_id
        self.group_id = group_id
        self.tasks_recieved = []
        self.tasks_finished = []
        
    def __str__(self):
        return ('user_id: %s, group_id: %s' % (self.user_id, self.group_id))
    

class NodeInterface(object):
    
    def __init__(self):
        self.node_id = uuid.uuid4()
        self.ip = None
        self.port = None
        self.num_cores = None
        self.num_running = None #for user side only
        self.num_queued = None  #for user side only
        self.tasks_sent = []    #for user side only
        self.params = {}
        
    def info(self):
        return {'node_id': str(self.node_id), 'ip': self.ip
                , 'port': self.port, 'num_cores': self.num_cores
                , 'num_running': self.num_running
                , 'num_queued':self.num_queued}
        
    def get_signature(self):
        return {'node_id': self.node_id, 'ip': self.ip
                , 'port': self.port}
        
    def update_counts(self):
        response = intercom.get_counts(self.ip, self.port)
        self.num_cores = response["num_cores"] if "num_cores" in response else 1
        self.num_running = response["num_tasks_running"] if "num_tasks_running" in response else 1
        self.num_queued = response["num_tasks_queued"] if "num_tasks_queued" in response else 1
        return response

    def update_info(self):
        response = intercom.get_node_info(self.ip, self.port)
        self.node_id = uuid.UUID(str(response['node_id'])) if 'node_id' in response else None
        self.ip = response['ip'] if 'ip' in response else None
        self.port = response['port'] if 'port' in response else None
        self.num_cores = response['num_cores'] if 'num_cores' in response else None
        self.num_running = response['num_running'] if 'num_running' in response else None
        self.num_queued = response['num_queued'] if 'num_queued' in response else None
        return response
    
    def add_task(self, task):
        response = intercom.post_task(self.ip, self.port, task, params=self.params)
        if (response['task_added']=='True'):
            self.tasks_sent.append(task)
            return True
        else:
            return False
    
    def get_num_cores(self):
        return self.num_cores
    
    def get_num_running(self):
        return self.num_running
    

class ClusterExecutor(NodeInterface):
    
    def __init__(self, ip, port):
        NodeInterface.__init__(self)
        self.ip = ip
        self.port = port
        self.user_id = None
        self.group_id = None
        
    def update_params(self):
        self.params = {'user_id': self.user_id, 'group_id': self.group_id}
        
    def connect(self, user_id, group_id='base'):
        response = intercom.connect_user(self.ip, self.port
                , params={'user_id': user_id, 'group_id': group_id})
        if (response['connected']==True):
            self.user_id = user_id
            self.group_id = group_id
            self.update_params()
            return True
        else:
            return False
        
    def __str__(self):
        return ('ip: %s, port: %s, user_id: %s, group_id: %s' 
                % (self.ip, self.port, self.user_id, self.group_id))
        