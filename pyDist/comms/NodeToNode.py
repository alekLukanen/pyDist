import json
from aiohttp import web

from pyDist.comms.Logging import Log


# receiver of incoming connections
class Receive(Log):

    def __init__(self):
        Log.__init__(self, __name__)
        self.logger.debug('Receive of NodeToNode')

    async def ntn_connect_node(self, request):
        self.logger.debug('called ce_connect_node')
        connection_data = json.loads(await request.text())
        response_data = self.interfaces.connect_node(connection_data)
        return web.Response(body=response_data, headers={"Content-Type": "application/json"})


# sender of outgoing communications (requests data from other sources)
class Send(Log):

    def __init__(self):
        Log.__init__(self, __name__)
        self.logger.debug('Send of NodeToNode')


# get basic data from here
class Status(Log):

    def __init__(self):
        Log.__init__(self, __name__)
        self.logger.debug('Status of NodeToNode')


class Comm(Receive, Send, Status):

    def __init__(self):
        Receive.__init__(self)
        Send.__init__(self)
        Status.__init__(self)
