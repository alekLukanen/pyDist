import uuid
from pyDist import pickleFunctions


class ClusterItem(object):

    def __init__(self):
        self.cluster_trace = []
        self.item_id = uuid.uuid4()
        self.interface_id = None

    def add_trace(self, signature):
        self.cluster_trace.append(signature)

    def pop_tracer(self):
        return self.cluster_trace.pop()


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
            self.flag = self.pickleVariable(self.flag)
            self.id = self.pickleVariable(self.id)
            self.ran = self.pickleVariable(self.ran)
            self.result = self.pickleVariable(self.result)
            self._done_callbacks = self.pickleVariable(self._done_callbacks)

            self._pickled_inner = True

    def unpickleInnerData(self):
        if self._pickled_inner:
            self.fn = self.unpickleVariable(self.fn)
            self.args = self.unpickleVariable(self.args)
            self.kwargs = self.unpickleVariable(self.kwargs)
            self.flag = self.unpickleVariable(self.flag)
            self.id = self.unpickleVariable(self.id)
            self.ran = self.unpickleVariable(self.ran)
            self.result = self.unpickleVariable(self.result)
            self._done_callbacks = self.unpickleVariable(self._done_callbacks)

            self._pickled_inner = False

    def pickle(self):
        pickle = pickleFunctions.createPickleServer(self)
        return pickle

    def __str__(self):
        return f'item_id: {self.item_id}, id(user defined): {self.id}, ran: {self.ran}, result: {self.result}'


class VariableItem(ClusterItem):

    def __init__(self, variable, ip, port):
        ClusterItem.__init__(self)
        self.variable = variable
        self.ip = ip
        self.port = port