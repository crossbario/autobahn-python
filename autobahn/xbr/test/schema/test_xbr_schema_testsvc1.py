import os
import pkg_resources
import txaio

if 'USE_TWISTED' in os.environ and os.environ['USE_TWISTED']:
    from twisted.trial import unittest

    txaio.use_twisted()
else:
    import unittest

    txaio.use_asyncio()

from autobahn.xbr import FbsRepository


class TestFbsBase(unittest.TestCase):
    """
    FlatBuffers tests base class, loads test schemas.
    """

    def setUp(self):
        self.repo = FbsRepository('autobahn')
        self.archives = []
        for fbs_file in ['demo.bfbs', 'trading.bfbs', 'testsvc1.bfbs', 'wamp-control.bfbs']:
            archive = pkg_resources.resource_filename('autobahn', 'xbr/test/catalog/schema/{}'.format(fbs_file))
            self.repo.load(archive)
            self.archives.append(archive)
