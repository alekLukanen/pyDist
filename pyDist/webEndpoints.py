
import aiohttp
import aiohttp_jinja2

node = None

@aiohttp_jinja2.template('index.jinja2')
async def splash_page(request):
    return {'interface_num_cores': node.interface.num_cores,
            'interfaces_num_users': len(node.interfaces.user_interfaces),
            'interfaces_server_interfaces': len(node.interfaces.node_interfaces),
            'interfaces_client_interfaces': len(node.interfaces.client_interfaces)}
#.server_interfaces = []
#        self.client_interfaces = []