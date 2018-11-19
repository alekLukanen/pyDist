
import threading

from pyDist import Interfaces, TaskManager
from pyDist.comms.Logging import Log


class WorkItemOptimizer(Log):

    def __init__(self, interface_holder: Interfaces.InterfaceHolder):
        Log.__init__(self, __name__)
        self.interfaces = interface_holder
        self.task_manager = TaskManager.TaskManager()

        self._condition = threading.Condition()  # makes the class thread-safe

    def add_work_item(self, work_item, data):
        """
        Add a work item to the node. The inner data
        of the work item should be pickled before being
        passed to this method.
        :param work_item:
        :param data
        :return: True or False for added
        """
        user = self.interfaces.find_user_by_user_id(data['user_id'])
        if user:
            user.add_received_work_item(work_item)
        else:
            self.logger.warning('THE USER DOES NOT EXIST, WORK ITEM NOT ADDED')
        self.execute_work_item(work_item)
        return True

    def execute_work_item(self, work_item):
        """
        Find a work item and execute it.
        Process -
            (1) add work item to nodes task manager
            (2) else send work item to another node
        :param work_item:
        :return: True or False for executed
        """
        pass

    def work_item_finished_callback(self, future):
        """
        Method called when a work item finishes.
        Process -
            (1) unpickle inner data
            (2) updated work item in user interface
            (3) remove item from task list in task manager
            (4) attempt to run another work item in the task manager
            (5) perform error checking
        :param future:
        :return:
        """
        pass

    async def find_open_node(self):
        """
        For all nodes in the interface holder find a node
        that has an open spot for a work item. That is, the node
        has an open core to execute a task.
        :return: a node interface or none
        """
        await self.interface_holder.update_node_interface_data()
        for node_id in self.interface_holder.node_interfaces:
            print('node_id: ', node_id)
            node_interface = self.interface_holder.node_interfaces[node_id]
            if node_interface.num_running < node_interface.num_cores:
                # the node has an open core send the work item to that core
                return node_interface
            else:
                # The node is already running the maximum it can.
                # Adding another work item would mean the work item
                # would be queued and might take longer to execute.
                continue
        return None

    async def send_work_item_to_node(self, work_item):
        """
        For a given work item attempt to send the item to an
        open node on the network of nodes.
        :param work_item: a work item on the current node
        :return: True or False
        """
        node = await self.find_open_node()  # find an open node
        if node:
            await node.add_work_item(work_item)  # send work item to the node through its interface
            return True
        return False
