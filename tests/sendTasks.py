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
    awi.SAMPLES = 10_000
    awi.submit_helper(1, 100, ip='192.168.0.19', port=9000)
    logger.debug('- tasks sent to the head node')