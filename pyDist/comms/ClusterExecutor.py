
import json
from aiohttp import web

import pyDist.Interfaces as Interfaces
from pyDist.comms.Logging import Log


# receiver of incoming connections
class Receive(Log):

    def __init__(self, interfaces: Interfaces.InterfaceHolder):
        Log.__init__(self)
        print('Receive of ClusterExecutor')
        self.interfaces = interfaces

    async def index(self, request):
        self.logger.debug('/')
        return web.Response(text='Hello Aiohttp!')

    async def connect_user(self, request):
        self.logger.debug('called connect_user')
        connection_data = json.loads(await request.text())
        response_data = self.interfaces.connect_user(connection_data)
        return web.Response(body=response_data, headers={"Content-Type": "application/json"})

    async def list_of_users(self, request):
        self.logger.debug('called list_of_users')
        data = json.dumps({'data': self.interfaces.get_interfaces_as_dict()})
        return web.Response(body=data, headers={"Content-Type": "application/json"})


# sender of outgoing communications (requests data from other sources)
class Send(object):

    def __init__(self):
        print('Send of ClusterExecutor')


class Status(object):

    def __init__(self):
        print('Receive of ClusterExecutor')


