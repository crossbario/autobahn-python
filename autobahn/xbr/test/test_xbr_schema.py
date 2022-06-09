import os
import copy
import pkg_resources
from random import randint, random
import txaio

if 'USE_TWISTED' in os.environ and os.environ['USE_TWISTED']:
    from twisted.trial import unittest
    txaio.use_twisted()
else:
    import unittest
    txaio.use_asyncio()

from autobahn.xbr._util import pack_ethadr, unpack_ethadr
from autobahn.xbr import FbsObject, FbsRepository
from autobahn.wamp.exception import InvalidPayload


class TestPackEthAdr(unittest.TestCase):
    def test_roundtrip(self):
        original_value = '0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047'
        packed_value = pack_ethadr(original_value)

        self.assertIsInstance(packed_value, dict)
        self.assertIn('value', packed_value)
        self.assertIsInstance(packed_value['value'], dict)
        for i in range(5):
            self.assertIn('w{}'.format(i), packed_value['value'])
            self.assertTrue(type(packed_value['value']['w{}'.format(i)]) == int)

        unpacked_value = unpack_ethadr(packed_value, return_str=True)
        self.assertEqual(unpacked_value, original_value)


class TestFbsBase(unittest.TestCase):
    def setUp(self):
        # self.archive = os.path.join(os.path.dirname(__file__), 'catalog', 'schema', 'demo.bfbs')
        self.archive = pkg_resources.resource_filename('autobahn', 'xbr/test/catalog/schema/demo.bfbs')
        self.repo = FbsRepository('autobahn')
        self.repo.load(self.archive)


class TestFbsRepository(TestFbsBase):

    def test_create_from_archive(self):
        self.assertTrue('uint160_t' in self.repo.objs)
        self.assertIsInstance(self.repo.objs['uint160_t'], FbsObject)

        # self.assertEqual(self.repo.total_count, 48)

        # self.assertTrue('trading.ClockTick' in self.repo.objs)
        # self.assertIsInstance(self.repo.objs['trading.ClockTick'], FbsObject)
        #
        # self.assertTrue('trading.ITradingClock' in self.repo.services)
        # self.assertIsInstance(self.repo.services['trading.ITradingClock'], FbsService)


class TestFbsValidateEthAddress(TestFbsBase):

    def test_validate_EthAddress_zero(self):

        for valid_value in [
            pack_ethadr('0x0000000000000000000000000000000000000000'),
            {
                'value': {
                    'w0': 0,
                    'w1': 0,
                    'w2': 0,
                    'w3': 0,
                    'w4': 0,
                }
            }
        ]:
            try:
                self.repo.validate(args=[valid_value],
                                   kwargs={},
                                   vt_args=['EthAddress'],
                                   vt_kwargs={})
            except Exception as exc:
                self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_EthAddress_valid(self):
        valid_value = pack_ethadr('0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047')

        try:
            self.repo.validate(args=[valid_value],
                               kwargs={},
                               vt_args=['EthAddress'],
                               vt_kwargs={})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_EthAddress_invalid(self):
        valid_value = pack_ethadr('0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047')

        self.assertRaisesRegex(InvalidPayload, 'invalid args length', self.repo.validate,
                               [], {},
                               ['EthAddress'], {})

        self.assertRaisesRegex(InvalidPayload, 'invalid kwargs length', self.repo.validate,
                               [valid_value], {'unexpected_kwarg': 23},
                               ['EthAddress'], {})

        self.assertRaisesRegex(InvalidPayload, 'unexpected key', self.repo.validate,
                               [{'value': valid_value['value'], 'invalid_key': 23}], {},
                               ['EthAddress'], {})

        self.assertRaisesRegex(InvalidPayload, 'unexpected key', self.repo.validate,
                               [{**valid_value, **{'invalid_key': 23}}], {},
                               ['EthAddress'], {})


class TestFbsValidateKeyValue(TestFbsBase):

    def test_validate_KeyValue_valid(self):
        valid_value = {
            'key': 'foo',
            'value': '23',
        }

        try:
            self.repo.validate(args=[valid_value],
                               kwargs={},
                               vt_args=['KeyValue'],
                               vt_kwargs={})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_KeyValue_invalid(self):
        valid_value = {
            'key': 'foo',
            'value': '23',
        }

        self.assertRaisesRegex(InvalidPayload, 'invalid args length', self.repo.validate,
                               [], {},
                               ['KeyValue'], {})

        self.assertRaisesRegex(InvalidPayload, 'invalid kwargs length', self.repo.validate,
                               [valid_value], {'unexpected_kwarg': '23'},
                               ['KeyValue'], {})

        self.assertRaisesRegex(InvalidPayload, 'invalid type', self.repo.validate,
                               [{'key': 'foo', 'value': 23}], {},
                               ['KeyValue'], {})

        self.assertRaisesRegex(InvalidPayload, 'unexpected key', self.repo.validate,
                               [{'key': 'foo', 'value': '23', 'invalid_key': '666'}], {},
                               ['KeyValue'], {})

        self.assertRaisesRegex(InvalidPayload, 'missing required field "key"', self.repo.validate,
                               [{'value': '23', 'invalid_key': '666'}], {},
                               ['KeyValue'], {})


class TestFbsValidateVoid(TestFbsBase):

    def test_validate_Void_valid(self):
        valid_adr = pack_ethadr('0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047')

        try:
            self.repo.validate(args=[],
                               kwargs={},
                               vt_args=[],
                               vt_kwargs={})
            self.repo.validate(args=[],
                               kwargs={},
                               vt_args=['Void'],
                               vt_kwargs={})
            self.repo.validate(args=[],
                               kwargs={},
                               vt_args=['Void', 'Void'],
                               vt_kwargs={})

            self.repo.validate(args=[{'value': valid_adr}],
                               kwargs={},
                               vt_args=['Void', 'EthAddress'],
                               vt_kwargs={})
            self.repo.validate(args=[{'value': valid_adr}],
                               kwargs={},
                               vt_args=['EthAddress', 'Void'],
                               vt_kwargs={})
            self.repo.validate(args=[{'value': valid_adr}],
                               kwargs={},
                               vt_args=['Void', 'EthAddress', 'Void'],
                               vt_kwargs={})
            self.repo.validate(args=[{'value': valid_adr}, {'value': valid_adr}],
                               kwargs={},
                               vt_args=['Void', 'EthAddress', 'EthAddress'],
                               vt_kwargs={})
            self.repo.validate(args=[{'value': valid_adr}, {'value': valid_adr}],
                               kwargs={},
                               vt_args=['EthAddress', 'Void', 'EthAddress'],
                               vt_kwargs={})

            self.repo.validate(args=[],
                               kwargs={},
                               vt_args=[],
                               vt_kwargs={'something': 'Void'})
            self.repo.validate(args=[],
                               kwargs={},
                               vt_args=[],
                               vt_kwargs={'something': 'Void', 'other': 'Void'})
            self.repo.validate(args=[],
                               kwargs={'owner': {'value': valid_adr}},
                               vt_args=[],
                               vt_kwargs={'something': 'Void', 'owner': 'EthAddress'})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_Void_invalid(self):
        valid_adr = pack_ethadr('0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047')

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
                               ['EthAddress', 'Void', 'EthAddress'], {})


class TestFbsValidateTestTableA(TestFbsBase):

    def test_validate_TestTableA_valid(self):
        valid_value = {
            'column1': True,
            'column2': randint(-127, -1),
            'column3': randint(1, 255),
            'column4': randint(-2 ** 15, -1),
            'column5': randint(1, 2 ** 16 - 1),
            'column6': randint(-2 ** 31, -1),
            'column7': randint(1, 2 ** 32 - 1),
            'column8': randint(-2 ** 63, -1),
            'column9': randint(1, 2 ** 64 - 1),
            'column10': 2.0 + random(),
            'column11': 2.0 + random(),
        }

        try:
            self.repo.validate(args=[valid_value],
                               kwargs={},
                               vt_args=['demo.TestTableA'],
                               vt_kwargs={})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_TestTableA_invalid(self):
        valid_value = {
            'column1': True,
            'column2': randint(-127, -1),
            'column3': randint(1, 255),
            'column4': randint(-2 ** 15, -1),
            'column5': randint(1, 2 ** 16 - 1),
            'column6': randint(-2 ** 31, -1),
            'column7': randint(1, 2 ** 32 - 1),
            'column8': randint(-2 ** 63, -1),
            'column9': randint(1, 2 ** 64 - 1),
            'column10': 2.0 + random(),
            'column11': 2.0 + random(),
        }

        # mandatory field with wrong type
        for i in range(len(valid_value)):
            # copy valid value, and set one column to a value of wrong type
            invalid_value = copy.copy(valid_value)
            if i == 0:
                # first column should be bool, so make it invalid with an int value
                invalid_value['column1'] = 666
            else:
                # all other columns are something different from bool, so make it invalid with a bool value
                invalid_value['column{}'.format(i + 1)] = True
            self.assertRaisesRegex(InvalidPayload, 'invalid type', self.repo.validate,
                                   [invalid_value], {},
                                   ['demo.TestTableA'], {})

        # mandatory field with wrong type `None`
        if True:
            for i in range(len(valid_value)):
                # copy valid value, and set one column to a value of wrong type
                invalid_value = copy.copy(valid_value)
                if i == 0:
                    # first column should be bool, so make it invalid with an int value
                    invalid_value['column1'] = None
                else:
                    # all other columns are something different from bool, so make it invalid with a bool value
                    invalid_value['column{}'.format(i + 1)] = None
                self.assertRaisesRegex(InvalidPayload, 'invalid type', self.repo.validate,
                                       [invalid_value], {},
                                       ['demo.TestTableA'], {})

        # mandatory field missing
        if True:
            for i in range(len(valid_value)):
                # copy valid value, and set one column to a value of wrong type
                invalid_value = copy.copy(valid_value)
                if i == 0:
                    # first column should be bool, so make it invalid with an int value
                    del invalid_value['column1']
                else:
                    # all other columns are something different from bool, so make it invalid with a bool value
                    del invalid_value['column{}'.format(i + 1)]
                self.assertRaisesRegex(InvalidPayload, 'missing required field', self.repo.validate,
                                       [invalid_value], {},
                                       ['demo.TestTableA'], {})
