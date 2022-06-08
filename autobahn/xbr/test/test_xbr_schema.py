import os
import txaio

if 'USE_TWISTED' in os.environ and os.environ['USE_TWISTED']:
    from twisted.trial import unittest
    txaio.use_twisted()
else:
    import unittest
    txaio.use_asyncio()

from autobahn.xbr import FbsService, FbsObject, FbsRepository
from autobahn.wamp.exception import InvalidPayload


class TestFbsRepository(unittest.TestCase):
    def setUp(self):
        self.archive = os.path.join(os.path.dirname(__file__), 'catalog', 'schema', 'trading.bfbs')
        self.repo = FbsRepository('autobahn')
        self.repo.load(self.archive)

    def test_create_from_archive(self):
        self.assertEqual(self.repo.total_count, 49)

        self.assertTrue('uint160_t' in self.repo.objs)
        self.assertIsInstance(self.repo.objs['uint160_t'], FbsObject)

        self.assertTrue('trading.ClockTick' in self.repo.objs)
        self.assertIsInstance(self.repo.objs['trading.ClockTick'], FbsObject)

        self.assertTrue('trading.ITradingClock' in self.repo.services)
        self.assertIsInstance(self.repo.services['trading.ITradingClock'], FbsService)

    def test_validate_address_valid(self):
        valid_adr = '0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047'

        try:
            self.repo.validate(args=[{'value': valid_adr}],
                               kwargs={},
                               vt_args=['Address'],
                               vt_kwargs={})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_address_invalid(self):
        valid_adr = '0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047'

        self.assertRaisesRegex(InvalidPayload, 'invalid args length', self.repo.validate,
                               [], {},
                               ['Address'], {})

        self.assertRaisesRegex(InvalidPayload, 'invalid kwargs length', self.repo.validate,
                               [{'value': valid_adr}], {'unexpected_kwarg': 23},
                               ['Address'], {})

        self.assertRaisesRegex(InvalidPayload, 'unexpected key', self.repo.validate,
                               [{'invalid_key': valid_adr}], {},
                               ['Address'], {})

    def test_validate_keyvalue_valid(self):
        valid_value = {
            'key': 'foo',
            'value': 23,
        }

        try:
            self.repo.validate(args=[valid_value],
                               kwargs={},
                               vt_args=['KeyValue'],
                               vt_kwargs={})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_keyvalue_invalid(self):
        valid_value = {
            'key': 'foo',
            'value': 23,
        }

        self.assertRaisesRegex(InvalidPayload, 'invalid args length', self.repo.validate,
                               [], {},
                               ['KeyValue'], {})

        self.assertRaisesRegex(InvalidPayload, 'invalid kwargs length', self.repo.validate,
                               [valid_value], {'unexpected_kwarg': 23},
                               ['KeyValue'], {})

        self.assertRaisesRegex(InvalidPayload, 'unexpected key', self.repo.validate,
                               [{'key': 'foo', 'value': 23, 'invalid_key': 666}], {},
                               ['KeyValue'], {})

        self.assertRaisesRegex(InvalidPayload, 'missing required field "key"', self.repo.validate,
                               [{'value': 23, 'invalid_key': 666}], {},
                               ['KeyValue'], {})

    def test_validate_void_valid(self):
        valid_adr = '0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047'
        try:
            self.repo.validate(args=[],
                               kwargs={},
                               vt_args=[],
                               vt_kwargs={})
            self.repo.validate(args=[],
                               kwargs={},
                               vt_args=['Void'],
                               vt_kwargs={})

            self.repo.validate(args=[{'value': valid_adr}],
                               kwargs={},
                               vt_args=['Void', 'Address'],
                               vt_kwargs={})
            self.repo.validate(args=[{'value': valid_adr}],
                               kwargs={},
                               vt_args=['Address', 'Void'],
                               vt_kwargs={})
            self.repo.validate(args=[{'value': valid_adr}],
                               kwargs={},
                               vt_args=['Void', 'Address', 'Void'],
                               vt_kwargs={})
            self.repo.validate(args=[{'value': valid_adr}, {'value': valid_adr}],
                               kwargs={},
                               vt_args=['Void', 'Address', 'Address'],
                               vt_kwargs={})
            self.repo.validate(args=[{'value': valid_adr}, {'value': valid_adr}],
                               kwargs={},
                               vt_args=['Address', 'Void', 'Address'],
                               vt_kwargs={})

            self.repo.validate(args=[],
                               kwargs={},
                               vt_args=[],
                               vt_kwargs={'something': 'Void'})
            self.repo.validate(args=[],
                               kwargs={'owner': {'value': valid_adr}},
                               vt_args=[],
                               vt_kwargs={'something': 'Void', 'owner': 'Address'})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_void_invalid(self):
        valid_adr = '0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047'

        self.assertRaisesRegex(InvalidPayload, 'invalid args length', self.repo.validate,
                               [23], {},
                               ['Void'], {})

        self.assertRaisesRegex(InvalidPayload, 'invalid args length', self.repo.validate,
                               [{}], {},
                               ['Void'], {})

        self.assertRaisesRegex(InvalidPayload, 'invalid args length', self.repo.validate,
                               [None], {},
                               ['Void'], {})

        self.assertRaisesRegex(InvalidPayload, 'invalid kwargs length', self.repo.validate,
                               [], {'unexpected_kwarg': 23},
                               ['Void'], {})

        self.assertRaisesRegex(InvalidPayload, 'invalid args length', self.repo.validate,
                               [{'value': valid_adr}], {},
                               ['Address', 'Void', 'Address'], {})
