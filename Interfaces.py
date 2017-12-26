#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 16:03:08 2017

@author: alek
"""

import json
import uuid
import logging
import sys

import pickleFunctions
import intercom

class InterfaceHolder(object):
    
    def __init__(self):
        logging.basicConfig(format='%(name)-12s:%(lineno)-3s | %(levelname)-8s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
        self.user_interfaces = []
        self.server_interfaces = []
        self.client_interfaces = []
        
    def connect_user(self, user_data):
        self.logger.debug('connecting user: %s' % user_data)
        user_interface = self.find_user_by_user_id(user_data['user_id'])
        if (user_interface==None):
            user_interface = UserInterface(user_data['user_id'], user_data['group_id'])
            self.user_interfaces.append(user_interface)
            return json.dumps( {'connected': True} )
        else:
            return json.dumps( {'connected': True} )
        
    def find_user_by_user_id(self, user_id):
        for user in self.user_interfaces:
            if (user.user_id==user_id):
                return user
        return None
        
    def find_user_task(self):
        for user in self.user_interfaces:
            if (len(user.tasks_recieved)>0):
                #run a task
                task = user.tasks_recieved.pop()
                return user, task
        return None, None
    
    def update_task_in_user(self, task):
        for user in self.user_interfaces:
            if (user.interface_id==task.interface_id):
                user.tasks_running.remove(task.task_id)
                user.tasks_finished.append(task)
                self.remove_task_in_user_by_task_id(user, task.task_id)
                return True
        return False
    
    def find_user_by_interface_id(self, interface_id):
        for user in self.user_interfaces:
            if (user.interface_id==interface_id):
                return user
        return None
    
    def remove_task_in_user_by_task_id(self, user, task_id):
        for task_rec in user.tasks_recieved:
            if (task_rec.task_id == task_id):
                user.tasks_reieved.remove(task_rec)
    
    def __str__(self):
        return ('#users: %d, #servers: %d, #clients: %d' 
                % (len(self.user_interfaces)
                , len(self.server_interfaces)
                , len(self.client_interfaces)))

class UserInterface(object):
    
    def __init__(self, user_id, group_id):
        self.interface_id = uuid.uuid4()
        self.user_id = user_id
        self.group_id = group_id
        self.tasks_recieved = []
        self.tasks_running  = []
        self.tasks_finished = []
       
    def counts(self):
        return ('#recv: %d, #running: %d, #fin: %d' 
                % (len(self.tasks_recieved)
                , len(self.tasks_running)
                , len(self.tasks_finished)))
        
    def __str__(self): 
        return ('user_id: %s, group_id: %s' 
               % (self.user_id, self.group_id))
    

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
        if (response['task_added']==True):
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
        