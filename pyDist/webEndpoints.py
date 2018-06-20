
import aiohttp
import aiohttp_jinja2

node = None

@aiohttp_jinja2.template('index.jinja2')
async def splash_page(request):
    return {'hello': f'world: {node.interface.num_queued}'}
