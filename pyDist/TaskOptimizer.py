
from pyDist import Interfaces

class TaskOptimizer(object):

    def __init__(self, interface_holder : Interfaces.InterfaceHolder):
        self.interface_holder = interface_holder

    def find_open_node(self):
        """
        For all nodes in the interface holder find a node
        that has an open spot for a task. That is, the node
        has an open core to execute a task.
        :return: a node interface or none
        """
        self.interface_holder.update_node_interface_data()
        for node_interface in self.interface_holder.node_interfaces:
            print('node_interface: ', node_interface)
            if node_interface.num_running < node_interface.num_cores:
                # the node has an open core send the work item to that core
                node_interface.add_work_item()
            else:
                # The node is already running the maximum it can.
                # Adding another work item would mean the work item
                # would be queued and might take longer to execute.
                continue

