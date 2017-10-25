#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 20:16:39 2017

@author: lukanen
"""

import logging
import sys
from flask import Flask, jsonify, request
from ServerContext import ServerContext, ElementTypes
import json

app = Flask(__name__)
example_node_index = 0

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)s - %(funcName)20s() ] - %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()
logger.debug('Creating the server context and waiting for the user to start the server')


sc = ServerContext()

@app.route('/addJob', methods=["POST"])
def add_job():
    json_data = json.loads( request.get_data(as_text=True) )
    sc.add_job_element(json_data)
    return 'job added'

@app.route('/addSlaveNode', methods=["POST"])
def add_slave_node():
    json_data = json.loads( request.get_data(as_text=True) ) #returns a dictionary
    sc.add_general_element({'type': ElementTypes.slave_node_recv,
                            'json_data': json_data})
    return 'slave noded added'

@app.route('/nodeCounts', methods=['GET'])
def node_counts():
    data = sc.get_node_counts()
    return data
    
@app.route('/nodeInfo', methods=['GET'])
def node_info():
    data = sc.get_node_info()
    return data
    
@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    sc.server_ended()
    return 'Server shutting down...'

def boot(host, port, node):
    sc.node_ref = node
    app.run(host=host,port=port)
    
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def process():
    logger.debug('running the main process')
    
    
    '''
if __name__ == '__main__':
    try:
        thread = threading.Thread(target=process)
        thread.start()
        boot()
    except KeyboardInterrupt:
        thread.join()
        logger.debug('process thread joined')
        
      '''  
    