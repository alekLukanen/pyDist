
import sys
sys.path.append('.')

import pyDist.endpointSetup


def construct_node(args):
    print('--- spawning a Node ---')
    print(f'|- num cores : {int(args[1])}')
    print(f'|- node ip : {args[2]} ')
    print(f'|- node port : {args[3]}')

    node = pyDist.endpointSetup.setup_cluster_node(num_cores=int(args[1]))
    node.set_ip_and_port(args[2], int(args[3]))  # need to set for node connections

    num_connections = int((len(args) - 4) / 2)

    for i in range(0, num_connections):
        ip_index = 4 + 2 * i
        port_index = 5 + 2 * i
        print(f'|- connect to ip : {args[ip_index]}')
        print(f'|- connect to port : {int(args[port_index])}')
        node.connect_to_node(args[ip_index], int(args[port_index]))

    # boot the node with the given connections
    node.boot(args[2], int(args[3]))


if __name__ == '__main__':
    construct_node(sys.argv)
