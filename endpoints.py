#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 16:43:16 2017

@author: alek
"""

from aiohttp import web

async def index(request):
    print ('here')
    return web.Response(text='Hello Aiohttp!')