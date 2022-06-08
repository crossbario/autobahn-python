import os
import txaio

if 'USE_TWISTED' in os.environ and os.environ['USE_TWISTED']:
    from twisted.trial import unittest
    txaio.use_twisted()
else:
    import unittest
    txaio.use_asyncio()

from autobahn.xbr import FbsService, FbsObject, FbsRepository


class TestFbsRepository(unittest.TestCase):
    def setUp(self):
        self.archive = os.path.join(os.path.dirname(__file__), 'schema', 'trading.bfbs')
        self.repo = FbsRepository('autobahn')
        self.repo.load(self.archive)

    def test_from_archive(self):
        self.assertEqual(self.repo.total_count, 49)

        self.assertTrue('uint160_t' in self.repo.objs)
        self.assertIsInstance(self.repo.objs['uint160_t'], FbsObject)

        self.assertTrue('trading.ClockTick' in self.repo.objs)
        self.assertIsInstance(self.repo.objs['trading.ClockTick'], FbsObject)

        self.assertTrue('trading.ITradingClock' in self.repo.services)
        self.assertIsInstance(self.repo.services['trading.ITradingClock'], FbsService)

    def test_validate(self):
        try:
            self.repo.validate(args=[{'value2': '0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047'}],
                               kwargs={},
                               vt_args=['Address'],
                               vt_kwargs={})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')
