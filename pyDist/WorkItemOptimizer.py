
import threading

from pyDist import Interfaces, TaskManager
from pyDist.comms.Logging import Log
import pyDist.Tasks as Tasks


class WorkItemOptimizer(Log):

    def __init__(self, interface_holder: Interfaces.InterfaceHolder, num_cores):
        Log.__init__(self, __name__)
        self.interfaces = interface_holder
        self.task_manager = TaskManager.TaskManager(num_cores=num_cores)
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
            self.execute_work_item(work_item, user)
        else:
            self.logger.warning('THE USER DOES NOT EXIST, WORK ITEM NOT ADDED')
            return False
        return True

    def add_network_item(self, work_item, data):
        self.interfaces.network_interface.add_received_work_item(work_item)
        self.execute_work_item(work_item, self.interfaces.network_interface)
        return True

    def execute_work_item(self, work_item, user):
        """
        Find a work item and execute it.
        Process -
            (1) add work item to nodes task manager
            (2) else send work item to another node
        :param work_item:
        :param user:
        :return: True or False for executed
        """
        #work_item.pickleInnerData()
        if len(self.task_manager.tasks) < self.task_manager.num_cores:
            future = self.task_manager.executor.submit(Tasks.caller_helper, work_item)
            future.add_done_callback(self.work_item_finished_callback)
            self.task_manager.submit(future)
            user.work_items_running.append(work_item.item_id)
            self.logger.debug('added work item to running list')
            return True
        else:
            self.logger.debug('attempt to execute a work item on another node')
            self.disperse_work_item()
            return False

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
        self.logger.debug('task_finished_callback() result: %s' % future)
        # get the work item from future and unpickle the inside of the work item
        work_item = future.result()
        work_item.unpickleInnerData()
        work_item.returning = True

        if work_item.in_cluster_network():
            self.logger.debug(f'the work item is from the network interface')
            self.interfaces.update_work_item_in_network(work_item)
            t_removed = self.task_manager.remove_work_item_from_task_list_by_id(work_item)
            node_t_added = self.run_work_item_from_network()
            t_added = self.run_work_item_from_user()

            if not t_removed:
                self.logger.warning('A FUTURE FAILED TO BE REMOVED')
            if not node_t_added:
                self.logger.debug('NETWORK TASK NOT RUN FROM QUEUED TASKS')
            if not t_added:
                self.logger.debug('TASK NOT RUN FROM QUEUED TASKS')

            #work_item.pickleInnerData()
            self.logger.debug(f'work_item: {work_item}')
            self.logger.debug(f'tracer: {work_item.pop_tracer()}')
            bounced = work_item.bounce_back()

            if not bounced:
                self.logger.warning('THE WORK ITEM WAS NOT BOUNCED BACK')

            # at this point the work item should have been updated in the
            # cluster network interface and sent back to the previous node
            # in the work item's trace stack.
            return

        # here is where the taskmanager is udated based on the
        # tasks finished callback.
        # subract one from the taskmanagers couter
        # add a done result to the task
        # update the task in user_tasks with the result
        # remove the future from the task list, this keeps the futures list small
        t_updated = self.interfaces.update_work_item_in_user(work_item)
        t_removed = self.task_manager.remove_work_item_from_task_list_by_id(work_item)
        t_added = self.run_work_item_from_user()

        # show warning messages when necessary
        self.logger.debug(f'test_nodeEndpoints.counts(): '
                          f'{self.interfaces.find_user_by_interface_id(work_item.interface_id).counts()}')
        if not t_updated:
            self.logger.warning('A TASK FAILED TO UPDATE')
        if not t_removed:
            self.logger.warning('A FUTURE FAILED TO BE REMOVED')
        if not t_added:
            self.logger.debug('TASK NOT RUN FROM QUEUED TASKS')

    def run_work_item_from_network(self):
        if len(self.task_manager.tasks) < self.task_manager.num_cores:
            network, work_item = self.interfaces.find_network_work_item()
            if network and work_item:
                future = self.task_manager.executor.submit(Tasks.caller_helper, work_item)
                future.add_done_callback(self.work_item_finished_callback)
                self.task_manager.submit(future)
                network.work_items_running.append(work_item.item_id)
                self.logger.debug('added work item to running list')
                return False
            else:
                return True
        else:
            ##SEND WORK ITEM TO ANOTHER NODE######
            self.logger.debug('attempt to execute a work item on another node')
            self.disperse_work_item()
            #################################

    def run_work_item_from_user(self):
        if len(self.task_manager.tasks) < self.task_manager.num_cores:
            user, work_item = self.interfaces.find_user_work_item()
            if user and work_item:
                future = self.task_manager.executor.submit(Tasks.caller_helper, work_item)
                future.add_done_callback(self.work_item_finished_callback)
                self.task_manager.submit(future)
                user.work_items_running.append(work_item.item_id)
                self.logger.debug('added work item to running list')
                return False
            else:
                return True
        else:
            ##SEND WORK ITEM TO ANOTHER NODE######
            self.logger.debug('attempt to execute a work item on another node')
            self.disperse_work_item()
            #################################

    def disperse_work_item(self):
        node = self.find_open_node()  # find an open node
        if node:
            user, work_item = self.interfaces.find_user_work_item()
            if user and work_item:
                sent = self.send_work_item_to_node(node, work_item)
                if sent:
                    self.logger.debug('C <--- C work item: %s' % work_item)
                    user.work_items_running.append(work_item.item_id)
                    return True  # work item sent; open node found
                else:
                    return False  # work item not sent; open node not found
            else:
                return False  # no work item and/or user

    def find_open_node(self):
        """
        For all nodes in the interface holder find a node
        that has an open spot for a work item. That is, the node
        has an open core to execute a task.
        :return: a node interface or none
        """
        self.interfaces.update_node_interface_data()
        for node_id in self.interfaces.node_interfaces:
            print('node_id: ', node_id)
            node_interface = self.interfaces.node_interfaces[node_id]
            if node_interface.num_running < node_interface.num_cores:
                # the node has an open core send the work item to that core
                return node_interface
            else:
                # The node is already running the maximum it can.
                # Adding another work item would mean the work item
                # would be queued and might take longer to execute.
                continue
        return None

    def send_work_item_to_node(self, node, work_item):
        """
        For a given work item attempt to send the item to an
        open node on the network of nodes.
        :param node: a node to send the work item to
        :param work_item: a work item on the current node
        :return: True or False
        """
        if node:
            node.add_work_item(work_item)  # send work item to the node through its interface
            return True
        return False
