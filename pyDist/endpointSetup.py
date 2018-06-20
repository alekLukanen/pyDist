

from aiohttp import web
import aiohttp_jinja2
import jinja2

from pyDist import clusterEndpoints, webEndpoints


def setupClusterEndpoints(app):
    app.router.add_route('GET', '/', clusterEndpoints.index)
    app.router.add_route('GET', '/counts', clusterEndpoints.counts)
    app.router.add_route('GET', '/nodeInfo', clusterEndpoints.node_info)
    app.router.add_route('GET', '/getFinishedTaskList', clusterEndpoints.get_finished_task_list)
    app.router.add_route('GET', '/getSingleTask', clusterEndpoints.get_single_task)
    app.router.add_route('POST', '/addTask', clusterEndpoints.add_task)
    app.router.add_route('POST', '/addStringMessage', clusterEndpoints.add_string_message)
    app.router.add_route('POST', '/connectUser', clusterEndpoints.connect_user)


def setupWebEndpoints(app):
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('templates/'))

    app.router.add_route('GET', '/splashPage.html', webEndpoints.splash_page)
