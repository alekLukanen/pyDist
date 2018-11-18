
import json
from aiohttp import web

from pyDist.comms.Logging import Log


# receiver of incoming connections
class Receive(Log):

    def __init__(self):
        Log.__init__(self, __name__)
        self.logger.debug('Receive of ClusterExecutor')

    async def ce_connect_user(self, request):
        self.logger.debug('called ce_connect_user')
        connection_data = json.loads(await request.text())
        response_data = self.interfaces.connect_user(connection_data)
        return web.Response(body=response_data, headers={"Content-Type": "application/json"})


# sender of outgoing communications (requests data from other sources)
class Send(Log):

    def __init__(self):
        Log.__init__(self, __name__)
        self.logger.debug('Send of ClusterExecutor')


# get basic data from here
class Status(Log):

    def __init__(self):
        Log.__init__(self, __name__)
        self.logger.debug('Receive of ClusterExecutor')

    async def ce_index(self, request):
        self.logger.debug('/')
        return web.Response(text='Hello from Status!')

    async def ce_stats(self, request):
        self.logger.debug('called ce_status')
        data = json.dumps({'data': {'num_users': len(self.interfaces.user_interfaces),
                           'num_nodes': len(self.interfaces.node_interfaces),
                          'num_clients': len(self.interfaces.client_interfaces)}})
        return web.Response(body=data, headers={"Content-Type": "application/json"})

    async def ce_list_of_users(self, request):
        self.logger.debug('called ce_list_of_users')
        self.logger.debug(f'self: {self}')
        self.logger.debug(f'self.interfaces: {self.interfaces}')
        data = json.dumps({'data': self.interfaces.get_interfaces_as_dict()})
        return web.Response(body=data, headers={"Content-Type": "application/json"})


class Comm(Receive, Send, Status):

    def __init__(self):
        Receive.__init__(self)
        Send.__init__(self)
        Status.__init__(self)
