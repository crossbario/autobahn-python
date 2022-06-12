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
from autobahn.xbr import FbsType, FbsObject, FbsService, FbsRPCCall, FbsRepository, FbsSchema, FbsField, FbsEnum, FbsEnumValue
from autobahn.wamp.exception import InvalidPayload


class TestPackEthAdr(unittest.TestCase):
    def test_roundtrip(self):
        raise unittest.SkipTest("FIXME")
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
        self.repo = FbsRepository('autobahn')
        self.archives = []
        for fbs_file in ['demo.bfbs', 'trading.bfbs', 'testsvc1.bfbs', 'wamp-control.bfbs']:
            archive = pkg_resources.resource_filename('autobahn', 'xbr/test/catalog/schema/{}'.format(fbs_file))
            self.repo.load(archive)
            self.archives.append(archive)


class TestFbsRepository(TestFbsBase):

    def test_create_from_archive(self):
        self.assertIn('uint160_t', self.repo.objs)
        self.assertIsInstance(self.repo.objs['uint160_t'], FbsObject)

        # self.assertEqual(self.repo.total_count, 69)

        self.assertIn('trading.ClockTick', self.repo.objs)
        self.assertIsInstance(self.repo.objs['trading.ClockTick'], FbsObject)

        self.assertIn('trading.ITradingClock', self.repo.services)
        self.assertIsInstance(self.repo.services['trading.ITradingClock'], FbsService)

        self.assertIn('testsvc1.TestRequest', self.repo.objs)
        self.assertIsInstance(self.repo.objs['testsvc1.TestRequest'], FbsObject)
        self.assertIn('testsvc1.TestResponse', self.repo.objs)
        self.assertIsInstance(self.repo.objs['testsvc1.TestResponse'], FbsObject)
        self.assertIn('testsvc1.ITestService1', self.repo.services)
        self.assertIsInstance(self.repo.services['testsvc1.ITestService1'], FbsService)

    def test_loaded_schema(self):
        schema_fn = pkg_resources.resource_filename('autobahn', 'xbr/test/catalog/schema/testsvc1.bfbs')

        # get reflection schema loaded
        schema: FbsSchema = self.repo.schemas[schema_fn]

        # get call from service defined in schema
        call: FbsRPCCall = schema.services['testsvc1.ITestService1'].calls['run_something1']

        # for each of the call request and call response type names ...
        call_type: FbsObject
        for call_type in [schema.objs[call.request.name], schema.objs[call.response.name]]:

            # ... iterate over all fields
            field: FbsField
            for field in call_type.fields_by_id:
                # we only need to process the "_type" fields auto-added for Union types
                if field.type.basetype == FbsType.UType:
                    assert field.name.endswith('_type')

                    # get the enum storing the Union
                    call_type_enum: FbsEnum = schema.enums_by_id[field.type.index]
                    assert call_type_enum.is_union

                    # get all enum values, which store Union types
                    union_type_value: FbsEnumValue
                    for union_type_value in call_type_enum.values:
                        if union_type_value != 'NONE':
                            # resolve union type value names in same namespace as containing union type [???]
                            if '.' in call_type_enum.name:
                                namespace = call_type_enum.name.split('.')[0]
                                union_type_qn = '{}.{}'.format(namespace, union_type_value)
                            else:
                                union_type_qn = union_type_value
                            # get type object for Union type by fully qualified name
                            union_type = schema.objs[union_type_qn]
                            print(union_type)

        # print(self.repo.objs['testsvc1.TestRequest'])
        # print(self.repo.enums['testsvc1.TestRequestAny'])
        # print(self.repo.objs['testsvc1.TestRequestArgument'])
        # print(self.repo.objs['testsvc1.TestRequestProgress'])
        # print()

        # print(self.repo.objs['testsvc1.TestResponse'])
        # print(self.repo.enums['testsvc1.TestResponseAny'])
        # print(self.repo.objs['testsvc1.TestResponseResult'])
        # print(self.repo.objs['testsvc1.TestResponseProgress'])
        # print(self.repo.objs['testsvc1.TestResponseError1'])
        # print(self.repo.objs['testsvc1.TestResponseError2'])
        # print()

        # svc1 = self.repo.services['testsvc1.ITestService1']
        # for key in svc1.calls.keys():
        #     ep: FbsRPCCall = svc1.calls[key]
        #     print(ep)

        # svc2 = self.repo.services['trading.ITradingClock']
        # for key in svc2.calls.keys():
        #     ep: FbsRPCCall = svc2.calls[key]
        #     print(ep)


class TestFbsValidateObjUint160(TestFbsBase):
    def test_validate_uint160_zero(self):
        valid_args = [0, 0, 0, 0, 0]

        try:
            self.repo.validate_obj('uint160_t', valid_args)
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

        try:
            self.repo.validate('uint160_t', args=valid_args, kwargs={})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_uint160_valid(self):
        element_max = 2 ** 32 - 1
        valid_args_list = [
            [0, 0, 0, 0, 0],
            [element_max, element_max, element_max, element_max, element_max],
            pack_ethadr('0x0000000000000000000000000000000000000000'),
            pack_ethadr('0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047'),
        ]
        try:
            for valid_args in valid_args_list:
                self.repo.validate('uint160_t', args=valid_args, kwargs={})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')


class TestFbsValidateObjRealmConfig(TestFbsBase):
    def setUp(self):
        super().setUp()
        self.realm_config1 = {
            "name": "realm1",
            "roles": [{
                "name": "anonymous",
                "permissions": [{
                    "uri": "",
                    "match": "prefix",
                    "allow": {
                        "call": True,
                        "register": True,
                        "publish": True,
                        "subscribe": True
                    },
                    "disclose": {
                        "caller": True,
                        "publisher": True
                    },
                    "cache": True
                }]
            }]
        }

    def test_validate_RealmConfig_valid(self):
        try:
            self.repo.validate_obj('wamp.RealmConfig', self.realm_config1)
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_RealmConfig_invalid(self):
        raise unittest.SkipTest("FIXME")

        config = copy.copy(self.realm_config1)
        config['roles'] = 666
        self.assertRaisesRegex(InvalidPayload, 'missing positional argument', self.repo.validate_obj,
                               'wamp.RealmConfig', config)

        config = copy.copy(self.realm_config1)
        del config['roles']
        config['foobar'] = 666
        self.assertRaisesRegex(InvalidPayload, 'missing positional argument', self.repo.validate_obj,
                               'wamp.RealmConfig', config)


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
                self.repo.validate('EthAddress', args=[valid_value], kwargs={})
            except Exception as exc:
                self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_EthAddress_valid(self):
        valid_value = pack_ethadr('0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047')

        try:
            self.repo.validate('EthAddress', args=[valid_value], kwargs={})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_EthAddress_invalid(self):
        raise unittest.SkipTest("FIXME")

        valid_value = pack_ethadr('0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047')

        self.assertRaisesRegex(InvalidPayload, 'missing positional argument', self.repo.validate,
                               'EthAddress', [], {})

        self.assertRaisesRegex(InvalidPayload, 'unexpected keyword arguments', self.repo.validate,
                               'EthAddress', [valid_value], {'unexpected_kwarg': 23})

        self.assertRaisesRegex(InvalidPayload, 'unexpected key', self.repo.validate,
                               'EthAddress', [{'value': valid_value['value'], 'invalid_key': 23}], {})

        self.assertRaisesRegex(InvalidPayload, 'unexpected key', self.repo.validate,
                               'EthAddress', [{**valid_value, **{'invalid_key': 23}}], {})


class TestFbsValidateKeyValue(TestFbsBase):

    def test_validate_KeyValue_valid(self):
        try:
            self.repo.validate('KeyValue', args=['foo', '23'], kwargs={})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_KeyValue_invalid(self):
        self.assertRaisesRegex(InvalidPayload, 'missing positional argument', self.repo.validate,
                               'KeyValue', [], {})

        self.assertRaisesRegex(InvalidPayload, 'missing positional argument', self.repo.validate,
                               'KeyValue', ['foo'], {})

        self.assertRaisesRegex(InvalidPayload, 'unexpected positional arguments', self.repo.validate,
                               'KeyValue', ['foo', '23', 'unexpected'], {})

        self.assertRaisesRegex(InvalidPayload, 'unexpected keyword arguments', self.repo.validate,
                               'KeyValue', ['foo', '23'], {'unexpected_kwarg': '23'})

        self.assertRaisesRegex(InvalidPayload, 'invalid positional argument type', self.repo.validate,
                               'KeyValue', ['foo', 23], {})

    def test_validate_KeyValues_valid(self):
        values = []

        # empty list
        try:
            self.repo.validate('KeyValues', args=[values], kwargs={})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

        # non-empty list
        for i in range(10):
            values.append(['key{}'.format(i), 'value{}'.format(i)])
        try:
            self.repo.validate('KeyValues', args=[values], kwargs={})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_KeyValues_invalid(self):
        invalid_values = [
            ([], {}),
            (['foo'], {}),
            (['foo', '23', 'unexpected'], {}),
            (['foo', '23'], {'unexpected_kwarg': '23'}),
            (['foo', 23], {})
        ]
        for args, kwargs in invalid_values:
            self.assertRaises(InvalidPayload, self.repo.validate, 'KeyValue', args, kwargs)

        values = []
        for i in range(10):
            values.append((['key{}'.format(i), 'value{}'.format(i)], {}))

        for args, kwargs in invalid_values:
            valid_values = copy.copy(invalid_values)
            valid_values.append((args, kwargs))
            self.repo.validate('KeyValues', args=[valid_values], kwargs={})


class TestFbsValidateVoid(TestFbsBase):

    def test_validate_Void_valid(self):
        try:
            self.repo.validate(None, args=[], kwargs={})
            self.repo.validate('Void', args=[], kwargs={})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_Void_invalid(self):
        valid_adr = pack_ethadr('0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047')

        self.assertRaisesRegex(InvalidPayload, 'unexpected positional argument', self.repo.validate,
                               'Void', [23], {})

        self.assertRaisesRegex(InvalidPayload, 'unexpected positional argument', self.repo.validate,
                               'Void', [{}], {})

        self.assertRaisesRegex(InvalidPayload, 'unexpected positional argument', self.repo.validate,
                               'Void', [None], {})

        self.assertRaisesRegex(InvalidPayload, 'unexpected positional argument', self.repo.validate,
                               'Void', [{'value': valid_adr}], {})

        self.assertRaisesRegex(InvalidPayload, 'unexpected keyword argument', self.repo.validate,
                               'Void', [], {'unexpected_kwarg': None})

        self.assertRaisesRegex(InvalidPayload, 'unexpected keyword argument', self.repo.validate,
                               'Void', [], {'unexpected_kwarg': 23})


class TestFbsValidateTestTableA(TestFbsBase):

    def test_validate_TestTableA_valid(self):
        valid_args = [
            True,
            randint(-127, -1),
            randint(1, 255),
            randint(-2 ** 15, -1),
            randint(1, 2 ** 16 - 1),
            randint(-2 ** 31, -1),
            randint(1, 2 ** 32 - 1),
            randint(-2 ** 63, -1),
            randint(1, 2 ** 64 - 1),
            2.0 + random(),
            2.0 + random(),
        ]

        try:
            self.repo.validate('demo.TestTableA', args=valid_args, kwargs={})
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_TestTableA_invalid(self):
        valid_args = [
            True,
            randint(-127, -1),
            randint(1, 255),
            randint(-2 ** 15, -1),
            randint(1, 2 ** 16 - 1),
            randint(-2 ** 31, -1),
            randint(1, 2 ** 32 - 1),
            randint(-2 ** 63, -1),
            randint(1, 2 ** 64 - 1),
            2.0 + random(),
            2.0 + random(),
        ]

        # mandatory field with wrong type
        for i in range(len(valid_args)):
            # copy valid value, and set one column to a value of wrong type
            invalid_args = copy.copy(valid_args)
            if i == 0:
                # first column should be bool, so make it invalid with an int value
                invalid_args[0] = 666
            else:
                # all other columns are something different from bool, so make it invalid with a bool value
                invalid_args[i] = True
            self.assertRaisesRegex(InvalidPayload, 'invalid positional argument type', self.repo.validate,
                                   'demo.TestTableA', invalid_args, {})

        # mandatory field with wrong type `None`
        if True:
            for i in range(len(valid_args)):
                # copy valid value, and set one column to a value of wrong type
                invalid_args = copy.copy(valid_args)
                invalid_args[i] = None
                self.assertRaisesRegex(InvalidPayload, 'invalid positional argument type', self.repo.validate,
                                       'demo.TestTableA', invalid_args, {})

        # mandatory field missing
        if True:
            for i in range(len(valid_args)):
                invalid_args = valid_args[:i]
                self.assertRaisesRegex(InvalidPayload, 'missing positional argument', self.repo.validate,
                                       'demo.TestTableA', invalid_args, {})
