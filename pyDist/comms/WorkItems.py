
import json
from aiohttp import web
import asyncio

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
        if work_item.returning:
            if work_item.in_cluster_network():
                # pass the work item along; this is a pass-through
                self.logger.debug('bouncing back to next node in trace')
                work_item.bounce_back()
            else:
                # try to add to user interfaces
                self.logger.debug('adding back to user interface for cluster interface pickup')

                # always pickle inner work item data here
                work_item.pickleInnerData()

                t_updated = self.work_item_optimizer.interfaces.update_work_item_in_user(work_item)
                t_added = self.work_item_optimizer.run_work_item_from_user()

                if not t_updated:
                    self.logger.warning('A TASK FAILED TO UPDATE')
                if not t_added:
                    self.logger.debug('TASK NOT RUN FROM QUEUED TASKS')

            data = json.dumps({'task_added': True})
            return web.Response(body=data, headers={"Content-Type": "application/json"})

        else:
            work_item.add_trace(self.interface.get_signature())  # sign the work item

            # always pickle inner work item data here
            work_item.pickleInnerData()

            # check if the work item has already been check-in at a head node
            if work_item.in_cluster_network():
                self.logger.debug(f'work_item added to pass-through list: {work_item}')
                added = self.work_item_optimizer.add_network_item(work_item, data)
            else:
                added = self.work_item_optimizer.add_work_item(work_item, data)

            data = json.dumps({'task_added': added})
            return web.Response(body=data, headers={"Content-Type": "application/json"})

    async def wi_get_single_work_item(self, request):
        self.logger.debug('called get single work item')
        params = request.rel_url.query

        # if the user_id parameter is not in the params list then
        # wait one second. This ensures that a single requester
        # does not take up all of the bandwidth to THIS node.
        if 'user_id' not in params:
            await asyncio.sleep(1)
            return json.dumps({'data': None, 'error': 'a user_id was not provided'})

        user = self.interfaces.find_user_by_user_id(params['user_id'])
        if user:
            await self.server_loop.run_in_executor(None, self.interfaces.wait_for_first_finished_work_item_for_user, user)
            work_item = self.interfaces.find_finished_work_item_for_user(user)
            self.interfaces.reset_finished_event_for_user(user)
            if work_item!=None:
                dictionary = {'data': work_item.pickle()}
                data = json.dumps(dictionary)
            else:
                self.logger.warning('the work item was of Nonetype')
                data = json.dumps({'data': None, 'error': 'work item was none'})
        else:
            data = json.dumps({'data': None, 'error': 'no test_nodeEndpoints for that user_id'})

        return web.Response(body=data, headers={"Content-Type": "application/json"})

    async def wi_shutdown_executor(self, request):
        self.logger.debug('called get shutdown executor')
        params = request.rel_url.query

        if 'shutdown' in params:
            data = params
            if params['shutdown']:
                self.logger.debug('shutting down the executor')
                # shutdown executor here
                self.shutdown_executor()
                ########################
            else:
                self.logger.debug('not shutting down the executor')
        else:
            data = json.dumps({'data': None, 'error': 'shutdown parameter not included in request'})

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

    async def wi_get_node_counts(self, request):
        self.logger.debug('called get node counts')
        params = request.rel_url.query
        num_cores = self.work_item_optimizer.task_manager.num_cores
        num_running = len(self.work_item_optimizer.task_manager.tasks)
        num_queued = len(self.work_item_optimizer.task_manager.queued_tasks)
        counts = {'num_cores': num_cores, 'num_tasks_running': num_running,
                  'num_tasks_queued': num_queued}
        data = json.dumps({'data': counts})
        return web.Response(body=data, headers={"Content-Type": "application/json"})

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
