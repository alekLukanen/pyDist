
import json
from aiohttp import web

from pyDist.comms.Logging import Log


# receiver of incoming connections
class Receive(Log):

    def __init__(self):
        Log.__init__(self, __name__)
        self.logger.debug('Receive of WorkItems')

    async def add_work_item(self, request):
        self.logger.debug('called add_work_item')
        request_data = json.loads(await request.text())


# sender of outgoing communications (requests data from other sources)
class Send(Log):

    def __init__(self):
        Log.__init__(self, __name__)
        self.logger.debug('Send of WorkItems')


# get basic data from here
class Status(Log):

    def __init__(self):
        Log.__init__(self, __name__)
        self.logger.debug('Receive of WorkItems')


class Comm(Receive, Send, Status):

    def __init__(self):
        Receive.__init__(self)
        Send.__init__(self)
        Status.__init__(self)
