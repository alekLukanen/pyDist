

import sys
sys.path.append('.')

import pyDist.endpointSetup

print('starting a ClusterExecutorNode...')

node = pyDist.endpointSetup.setup_cluster_node()
node.set_ip_and_port('192.168.0.12', 9001)
node.connect_to_node('192.168.0.19', 9000)
node.boot('192.168.0.12', 9001)
