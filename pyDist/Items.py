import uuid
import asyncio
from pyDist import pickleFunctions, intercom, stateless_intercom


class ClusterItem(object):

    def __init__(self):
        self.cluster_trace = []
        self.stored_cluster_trace = []
        self.item_id = uuid.uuid4()
        self.interface_id = None
        self.returning = False

    def trace(self):
        return self.stored_cluster_trace

    def in_cluster_network(self):
        return len(self.cluster_trace) > 1

    def add_trace(self, signature):
        self.cluster_trace.append(signature)
        self.stored_cluster_trace.append(signature)

    def pop_tracer(self):
        if len(self.cluster_trace) > 0:
            return self.cluster_trace.pop()
        else:
            return None

    def bounce_back(self, params={}):
        if self.returning:
            tracer = self.pop_tracer()
            if tracer:
                #post_work_item(server_ip, server_port, task, params={})
                io_loop = asyncio.new_event_loop()
                response = stateless_intercom.post_work_item(tracer['ip'], tracer['port'], self, params=params)
                if response['task_added']:
                    return True
                else:
                    return False  # work item not added
            else:
                return False  # tracer is none; no tracer left
        else:
            return False  # the work item is not returning back to the original node


class WorkerItem(ClusterItem):

    def __init__(self, fn, args, kwargs):
        ClusterItem.__init__(self)

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.flag = None
        self.id = None

        self.ran = False
        self.result = None
        self._done_callbacks = []

        self._pickled_inner = False

    def set_ran(self):
        self.ran = True
        self.returning = True

    def set_result(self, result):
        self.result = result

    def pickleVariable(self, var):
        return pickleFunctions.createPickleServer(var)

    def unpickleVariable(self, var):
        return pickleFunctions.unPickleServer(var)

    def pickleInnerData(self):
        if not self._pickled_inner:
            self.fn = self.pickleVariable(self.fn)
            self.args = self.pickleVariable(self.args)
            self.kwargs = self.pickleVariable(self.kwargs)
            #self.flag = self.pickleVariable(self.flag)
            #self.id = self.pickleVariable(self.id)
            #self.ran = self.pickleVariable(self.ran)
            self.result = self.pickleVariable(self.result)
            self._done_callbacks = self.pickleVariable(self._done_callbacks)

            self._pickled_inner = True

    def unpickleInnerData(self):
        if self._pickled_inner:
            self.fn = self.unpickleVariable(self.fn)
            self.args = self.unpickleVariable(self.args)
            self.kwargs = self.unpickleVariable(self.kwargs)
            #self.flag = self.unpickleVariable(self.flag)
            #self.id = self.unpickleVariable(self.id)
            #self.ran = self.unpickleVariable(self.ran)
            self.result = self.unpickleVariable(self.result)
            self._done_callbacks = self.unpickleVariable(self._done_callbacks)

            self._pickled_inner = False

    def pickle(self):
        self.pickleInnerData()
        pickle = pickleFunctions.createPickleServer(self)
        return pickle

    def createDictionary(self):
        return {'data': self.pickle()}

    def __str__(self):
        return f'item_id: {self.item_id}, id(test_nodeEndpoints defined): {self.id}' \
               f', hops: {len(self.cluster_trace)}' \
               f', ran: {self.ran}, result: {self.result}'


class VariableItem(ClusterItem):

    def __init__(self, variable, ip, port):
        ClusterItem.__init__(self)
        self.variable = variable
        self.ip = ip
        self.port = port
