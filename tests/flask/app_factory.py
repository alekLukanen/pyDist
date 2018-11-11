#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  9 21:15:12 2018

@author: alek
"""

from flask import Flask

class Data(object):
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def to_string(self):
        return f'Data(x,y) : ({self.x},{self.y})'

def create_app(name, config_filename):
    app = Flask(name)
    app.config.from_pyfile(config_filename)
    app.config['data'] = Data(1,2)
    
    from admin import admin
    app.register_blueprint(admin)
    
    return app
    
if __name__ == '__main__':
    print ('App Factory Test')
    app = create_app('app1', 'config.py')
    app.run(host='0.0.0.0',port=9000)