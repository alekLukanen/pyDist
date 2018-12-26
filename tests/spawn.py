
import sys
sys.path.append('.')

import pyDist.endpointSetup



print('--- spawning a Node ---')
print(f'|- node ip : {sys.argv[1]} ')
print(f'|- node port : {sys.argv[2]}')

node = pyDist.endpointSetup.setup_cluster_node(num_cores=4)
node.set_ip_and_port(sys.argv[1], int(sys.argv[2])) # need to set for node connections

num_connections = int((len(sys.argv)-3)/2)

for i in range(0, num_connections):
    ip_index = 3+2*i
    port_index = 4+2*i
    print(f'|- connect to ip : {sys.argv[ip_index]}')
    print(f'|- connect to port : {sys.argv[port_index]}')
    node.connect_to_node(sys.argv[ip_index], int(sys.argv[port_index]))

# boot the node with the given connections
node.boot(sys.argv[1], int(sys.argv[2]))
