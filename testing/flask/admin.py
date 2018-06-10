#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  9 21:17:27 2018

@author: alek
"""

from flask import current_app, Blueprint, render_template
admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
def index():
    print (current_app)
    current_app.config['data'].x +=1
    current_app.config['data'].y +=1
    return current_app.config['data'].to_string()