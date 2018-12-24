import asyncio
import sys
sys.path.append('.')

from pyDist import intercom

io_loop = asyncio.get_event_loop()

interfaces_from_9000 = io_loop.run_until_complete(intercom.get_interface_holder_interfaces('0.0.0.0', 9000))

print(interfaces_from_9000)
