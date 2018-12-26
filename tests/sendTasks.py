import logging
import sys
sys.path.append('.')

import tests.test_nodeEndpoints.add_work_items as awi

#logging utility
logging.getLogger("Nodes").setLevel(logging.WARNING)
logging.getLogger("endpoints").setLevel(logging.WARNING)
logging.basicConfig(format='%(name)-12s:%(lineno)-3s | %(levelname)-8s | %(message)s'
                , stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.debug('--- sendingTasks.py ---')
    logger.debug('- connecting 1 executor (user) and sending 12 tasks')
    awi.SAMPLES = 1_000_000
    ip = sys.argv[1]
    port = int(sys.argv[2])
    awi.submit_helper(1, 200, ip=ip, port=port)
    logger.debug('- tasks sent to the head node')
