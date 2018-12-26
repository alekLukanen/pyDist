
import sys
sys.path.append('.')

import pyDist.endpointSetup



print('--- spawning a Node ---')
print(f'|- num cores : {int(sys.argv[1])}')
print(f'|- node ip : {sys.argv[2]} ')
print(f'|- node port : {sys.argv[3]}')

node = pyDist.endpointSetup.setup_cluster_node(num_cores=int(sys.argv[1]))
node.set_ip_and_port(sys.argv[2], int(sys.argv[3]))  # need to set for node connections

num_connections = int((len(sys.argv)-4)/2)

for i in range(0, num_connections):
    ip_index = 4+2*i
    port_index = 5+2*i
    print(f'|- connect to ip : {sys.argv[ip_index]}')
    print(f'|- connect to port : {int(sys.argv[port_index])}')
    node.connect_to_node(sys.argv[ip_index], int(sys.argv[port_index]))

# boot the node with the given connections
node.boot(sys.argv[2], int(sys.argv[3]))
