
import json
from aiohttp import web

from pyDist.comms.Logging import Log
from pyDist import pickleFunctions

# receiver of incoming connections
class Receive(Log):

    def __init__(self):
        Log.__init__(self, __name__)
        self.logger.debug('Receive of WorkItems')

    async def wi_add_work_item(self, request):
        self.logger.debug('called add_work_item')
        data = json.loads(await request.text())
        work_item = pickleFunctions.unPickleServer(data['data'])
        work_item.add_trace(self.interface.get_signature())  # sign the work item

        # always pickle inner work item data here
        work_item.pickleInnerData()

        added = self.work_item_optimizer.add_work_item(work_item, data)

        data = json.dumps({'task_added': added})
        return web.Response(body=data, headers={"Content-Type": "application/json"})


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

    async def wi_get_user_counts(self, request):
        self.logger.debug('called get user counts')
        params = request.rel_url.query
        self.logger.debug(f'params: {params}')
        user = self.interfaces.find_user_by_user_id(params['user_id']) if 'user_id' in params else None
        counts = user.counts_dict() if user else {}
        data = json.dumps({'data': counts})
        return web.Response(body=data, headers={"Content-Type": "application/json"})


class Comm(Receive, Send, Status):

    def __init__(self):
        Receive.__init__(self)
        Send.__init__(self)
        Status.__init__(self)
