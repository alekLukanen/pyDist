
from pyDist import Interfaces

class WorkItemOptimizer(object):

    def __init__(self, interface_holder: Interfaces.InterfaceHolder):
        self.interface_holder = interface_holder

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
