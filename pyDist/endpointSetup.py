

from aiohttp import web
import aiohttp_jinja2
import jinja2
import multiprocessing

from pyDist import clusterEndpoints, webEndpoints, Nodes


def setup_cluster_node(num_cores=multiprocessing.cpu_count()):
    node = Nodes.ClusterNodeV2(num_cores=num_cores)
    node.app.router.add_route('POST', '/connectUser', node.ce_connect_user)
    node.app.router.add_route('POST', '/addWorkItem', node.wi_add_work_item)

    node.app.router.add_route('GET', '/', node.ce_index)
    node.app.router.add_route('GET', '/listOfUsers', node.ce_list_of_users)
    node.app.router.add_route('GET', '/interfaceStats', node.ce_stats)
    node.app.router.add_route('GET', '/userCounts', node.wi_get_user_counts)
    node.app.router.add_route('GET', '/counts', node.wi_get_node_counts)

    # these are two different routs going to the same method
    node.app.router.add_route('GET', '/getSingleWorkItem', node.wi_get_single_work_item)
    node.app.router.add_route('GET', '/getSingleTask', node.wi_get_single_work_item)
    node.app.router.add_route('POST', '/shutdownExecutor', node.wi_shutdown_executor)

    node.app.router.add_route('POST', '/connectNode', node.ntn_connect_node)
    node.app.router.add_route('GET', '/getInterfaceHolderInterfaces', node.ce_interface_holder_interfaces)

    return node


def setupClusterEndpoints(app):
    app.router.add_route('GET', '/', clusterEndpoints.index)
    app.router.add_route('GET', '/counts', clusterEndpoints.counts)
    app.router.add_route('GET', '/nodeInfo', clusterEndpoints.node_info)
    app.router.add_route('GET', '/getFinishedTaskList', clusterEndpoints.get_finished_task_list)
    app.router.add_route('GET', '/getSingleTask', clusterEndpoints.get_single_task)
    app.router.add_route('GET', '/getInterfaceHolderInterfaces', clusterEndpoints.get_interface_holder_interfaces)

    app.router.add_route('POST', '/addWorkItem', clusterEndpoints.add_work_item)
    app.router.add_route('POST', '/addStringMessage', clusterEndpoints.add_string_message)
    app.router.add_route('POST', '/connectUser', clusterEndpoints.connect_user)
    app.router.add_route('POST', '/connectNode', clusterEndpoints.connect_node)


def setupWebEndpoints(app):
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('templates/'))

    app.router.add_route('GET', '/splashPage.html', webEndpoints.splash_page)
