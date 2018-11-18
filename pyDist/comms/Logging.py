
import logging
import sys

logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)


class Log(object):

    def __init__(self):
        logging.basicConfig(format='%(name)-12s:%(lineno)-3s | %(levelname)-8s | %(message)s'
                            , stream=sys.stdout, level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
