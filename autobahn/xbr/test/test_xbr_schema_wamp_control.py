import os
import copy
import pkg_resources
from binascii import a2b_hex
from random import randint, random
import txaio

if 'USE_TWISTED' in os.environ and os.environ['USE_TWISTED']:
    from twisted.trial import unittest

    txaio.use_twisted()
else:
    import unittest

    txaio.use_asyncio()

from autobahn.xbr._util import pack_ethadr, unpack_ethadr
from autobahn.xbr import FbsType, FbsObject, FbsService, FbsRPCCall, FbsRepository, FbsSchema, FbsField, FbsEnum, \
    FbsEnumValue
from autobahn.wamp.exception import InvalidPayload


class TestFbsBase(unittest.TestCase):
    """
    FlatBuffers tests base class, loads test schemas.
    """

    def setUp(self):
        self.repo = FbsRepository('autobahn')
        self.archives = []
        for fbs_file in ['wamp-control.bfbs']:
            archive = pkg_resources.resource_filename('autobahn', 'xbr/test/catalog/schema/{}'.format(fbs_file))
            self.repo.load(archive)
            self.archives.append(archive)


class TestFbsValidatePermissionAllow(TestFbsBase):

    def test_validate_PermissionAllow_valid(self):
        tests = [
            {
                'call': True,
                'register': True,
                'publish': True,
                'subscribe': True
            },
            {
                'call': False,
                'register': False,
                'publish': False,
                'subscribe': False
            },
        ]
        for value in tests:
            try:
                self.repo.validate_obj('wamp.PermissionAllow', value)
            except Exception as exc:
                self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_PermissionAllow_invalid(self):
        tests = [
            (None, 'invalid type'),
            (666, 'invalid type'),
            (True, 'invalid type'),
            ({'some_unexpected_key': 666}, 'unexpected argument'),
            ({'call': True, 'register': True, 'publish': True}, 'missing argument'),
            ({'call': True, 'register': True, 'publish': True, 'subscribe': 666}, 'invalid type'),
            ({'call': True, 'register': True, 'publish': True, 'subscribe': None}, 'invalid type'),
            ({'call': True, 'register': True, 'publish': True, 'subscribe': True, 'some_unexpected_key': 666},
             'unexpected argument'),
        ]
        for value, expected_regex in tests:
            self.assertRaisesRegex(InvalidPayload, expected_regex,
                                   self.repo.validate_obj, 'wamp.PermissionAllow', value)


class TestFbsValidateRolePermission(TestFbsBase):

    def test_validate_RolePermission_valid(self):
        tests = [
            {},
            {
                'uri': 'com.example.',
                'match': 'prefix',
                'allow': {
                    'call': True,
                    'register': True,
                    'publish': True,
                    'subscribe': True
                },
                'disclose': {
                    'caller': True,
                    'publisher': True,
                },
                'cache': True
            },
        ]
        for value in tests:
            try:
                self.repo.validate_obj('wamp.RolePermission', value)
            except Exception as exc:
                self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_validate_RolePermission_invalid(self):
        tests = [
            (None, 'invalid type'),
            ({'some_unexpected_key': True}, 'unexpected argument'),
            ({'uri': 'com.example.', 'allow': {'some_unexpected_key': True}}, 'unexpected argument'),
            ({'uri': 666}, 'invalid type'),
            ({'uri': 'com.example.', 'match': 'prefix', 'allow': {'call': 666}}, 'invalid type'),
            ({'uri': 666, 'match': 'prefix',
              'allow': {'call': True, 'register': True, 'publish': True, 'subscribe': True},
              'disclose': {'caller': True, 'publisher': True}, 'cache': True}, 'invalid type'),
        ]
        for value, expected_regex in tests:
            self.assertRaisesRegex(InvalidPayload, expected_regex,
                                   self.repo.validate_obj, 'wamp.RolePermission', value)


class TestFbsValidateRoleConfig(TestFbsBase):
    def setUp(self):
        super().setUp()
        self.role_config1 = {
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
        }

    def test_RoleConfig_valid(self):
        try:
            self.repo.validate_obj('wamp.RoleConfig', self.role_config1)
        except Exception as exc:
            self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

    def test_RoleConfig_invalid(self):
        config = copy.copy(self.role_config1)
        config['name'] = 666
        self.assertRaisesRegex(InvalidPayload, 'invalid type', self.repo.validate_obj,
                               'wamp.RoleConfig', config)

        # config = copy.copy(self.realm_config1)
        # del config['roles']
        # config['foobar'] = 666
        # self.assertRaisesRegex(InvalidPayload, 'missing positional argument', self.repo.validate_obj,
        #                        'wamp.RealmConfig', config)


if False:
    class TestFbsValidateRealmConfig(TestFbsBase):
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

        def test_RealmConfig_valid(self):
            try:
                self.repo.validate_obj('wamp.RealmConfig', self.realm_config1)
            except Exception as exc:
                self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')

        def test_RealmConfig_invalid(self):
            config = copy.copy(self.realm_config1)
            config['name'] = 666
            self.assertRaisesRegex(InvalidPayload, 'invalid type', self.repo.validate_obj,
                                   'wamp.RealmConfig', config)

            # config = copy.copy(self.realm_config1)
            # del config['roles']
            # config['foobar'] = 666
            # self.assertRaisesRegex(InvalidPayload, 'missing positional argument', self.repo.validate_obj,
            #                        'wamp.RealmConfig', config)

        def test_start_router_realm_valid(self):
            valid_args = ['realm023', self.realm_config1]
            # valid_args = ['realm023', 23]
            try:
                self.repo.validate('wamp.StartRealm', args=valid_args, kwargs={})
            except Exception as exc:
                self.assertTrue(False, f'Inventory.validate() raised an exception: {exc}')
