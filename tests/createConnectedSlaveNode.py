

import sys
sys.path.append('.')

import pyDist.endpointSetup

print('starting a ClusterExecutorNode...')

node = pyDist.endpointSetup.setup_cluster_node()
node.connect_to_node('0.0.0.0', 9000)
node.boot('0.0.0.0', 9001)
