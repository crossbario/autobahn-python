import os
import sys
from unittest import skipIf
from unittest.mock import MagicMock

from twisted.trial.unittest import TestCase
from twisted.internet.defer import inlineCallbacks

from autobahn.xbr import HAS_XBR
from autobahn.wamp.cryptosign import HAS_CRYPTOSIGN

if HAS_XBR and HAS_CRYPTOSIGN:
    from autobahn.xbr._frealm import Seeder, FederatedRealm
    from autobahn.xbr._secmod import SecurityModuleMemory, EthereumKey
    from autobahn.wamp.cryptosign import CryptosignKey

# https://web3py.readthedocs.io/en/stable/providers.html#infura-mainnet
HAS_INFURA = 'WEB3_INFURA_PROJECT_ID' in os.environ and len(os.environ['WEB3_INFURA_PROJECT_ID']) > 0

# TypeError: As of 3.10, the *loop* parameter was removed from Lock() since it is no longer necessary
IS_CPY_310 = sys.version_info.minor == 10


@skipIf(not os.environ.get('USE_TWISTED', False), 'only for Twisted')
@skipIf(not HAS_INFURA, 'env var WEB3_INFURA_PROJECT_ID not defined')
@skipIf(not (HAS_XBR and HAS_CRYPTOSIGN), 'package autobahn[encryption,xbr] not installed')
class TestFederatedRealm(TestCase):

    gw_config = {
        'type': 'infura',
        'key': os.environ.get('WEB3_INFURA_PROJECT_ID', ''),
        'network': 'mainnet',
    }

    # "builtins.TypeError: As of 3.10, the *loop* parameter was removed from Lock() since
    # it is no longer necessary"
    #
    # solved via websockets>=10.3, but web3==5.29.0 requires websockets<10
    #
    @skipIf(IS_CPY_310, 'Web3 v5.29.0 (web3.auto.infura) raises TypeError on Python 3.10')
    def test_frealm_ctor_auto(self):
        name = 'wamp-proto.eth'

        fr = FederatedRealm(name)
        self.assertEqual(fr.status, 'STOPPED')
        self.assertEqual(fr.name_or_address, name)
        self.assertEqual(fr.gateway_config, None)
        self.assertEqual(fr.name_category, 'ens')

    def test_frealm_ctor_gw(self):
        name = 'wamp-proto.eth'

        fr = FederatedRealm(name, self.gw_config)
        self.assertEqual(fr.status, 'STOPPED')
        self.assertEqual(fr.name_or_address, name)
        self.assertEqual(fr.gateway_config, self.gw_config)
        self.assertEqual(fr.name_category, 'ens')

    @inlineCallbacks
    def test_frealm_initialize(self):
        name = 'wamp-proto.eth'
        fr1 = FederatedRealm(name, self.gw_config)

        self.assertEqual(fr1.status, 'STOPPED')
        yield fr1.initialize()
        self.assertEqual(fr1.status, 'RUNNING')

        self.assertEqual(fr1.address, '0x66267d0b1114cFae80C37942177a846d666b114a')

    def test_frealm_seeders(self):
        fr1 = MagicMock()
        fr1.name_or_address = 'wamp-proto.eth'
        fr1.address = '0x66267d0b1114cFae80C37942177a846d666b114a'
        fr1.status = 'RUNNING'
        fr1.seeders = [
            Seeder(frealm=fr1,
                   endpoint='wss://frealm1.example.com/ws',
                   label='Example Inc.',
                   operator='0xf5fb56886f033855C1a36F651E927551749361bC',
                   country='US'),
            Seeder(frealm=fr1,
                   endpoint='wss://fr1.foobar.org/ws',
                   label='Foobar Foundation',
                   operator='0xe59C7418403CF1D973485B36660728a5f4A8fF9c',
                   country='DE'),
            Seeder(frealm=fr1,
                   endpoint='wss://public-frealm1.pierre.fr:443',
                   label='Pierre PP',
                   operator='0x254dffcd3277C0b1660F6d42EFbB754edaBAbC2B',
                   country='FR'),
        ]
        self.assertEqual(len(fr1.seeders), 3)

        transports = [s.endpoint for s in fr1.seeders]
        self.assertEqual(transports, ['wss://frealm1.example.com/ws', 'wss://fr1.foobar.org/ws',
                                      'wss://public-frealm1.pierre.fr:443'])

    @inlineCallbacks
    def test_frealm_secmod(self):
        name = 'wamp-proto.eth'
        seedphrase = "myth like bonus scare over problem client lizard pioneer submit female collect"

        sm = SecurityModuleMemory.from_seedphrase(seedphrase)
        yield sm.open()
        self.assertEqual(len(sm), 2)
        self.assertTrue(isinstance(sm[0], EthereumKey), 'unexpected type {} at index 0'.format(type(sm[0])))
        self.assertTrue(isinstance(sm[1], CryptosignKey), 'unexpected type {} at index 1'.format(type(sm[1])))

        fr = FederatedRealm(name, self.gw_config)

        # FIXME
        fr._seeders = [
            Seeder(frealm=fr,
                   endpoint='wss://frealm1.example.com/ws',
                   label='Example Inc.',
                   operator='0xf5fb56886f033855C1a36F651E927551749361bC',
                   country='US'),
            Seeder(frealm=fr,
                   endpoint='wss://fr1.foobar.org/ws',
                   label='Foobar Foundation',
                   operator='0xe59C7418403CF1D973485B36660728a5f4A8fF9c',
                   country='DE'),
            Seeder(frealm=fr,
                   endpoint='wss://public-frealm1.pierre.fr:443',
                   label='Pierre PP',
                   operator='0x254dffcd3277C0b1660F6d42EFbB754edaBAbC2B',
                   country='FR'),
        ]

        yield fr.initialize()
        self.assertEqual(fr.status, 'RUNNING')
        self.assertEqual(fr.address, '0x66267d0b1114cFae80C37942177a846d666b114a')
        self.assertEqual(len(fr.seeders), 3)

        delegate_key = sm[0]
        client_key = sm[1]
        authextra = yield fr.seeders[0].create_authextra(client_key=client_key,
                                                         delegate_key=delegate_key,
                                                         bandwidth_requested=512,
                                                         channel_id=None,
                                                         channel_binding=None)

        self.assertEqual(authextra.get('pubkey', None), client_key.public_key(binary=False))

        # print(authextra)

        self.assertTrue('signature' in authextra)
        self.assertTrue(type(authextra['signature']) == str)
        self.assertEqual(len(authextra['signature']), 65 * 2)

# @skipIf(not os.environ.get('WAMP_ROUTER_URLS', None), 'WAMP_ROUTER_URLS not defined')
# @skipIf(not os.environ.get('USE_TWISTED', False), 'only for Twisted')
# @skipIf(not HAS_XBR, 'package autobahn[xbr] not installed')
# class TestFederatedRealmNetworked(TestCase):
#
#     def test_seeders_multi_reconnect(self):
#         from autobahn.twisted.component import Component, run
#
#         # WAMP_ROUTER_URLS=ws://localhost:8080/ws,ws://localhost:8081/ws,ws://localhost:8082/ws
#         # crossbar start --cbdir=./autobahn/xbr/test/.crossbar --config=config1.json
#         transports = os.environ.get('WAMP_ROUTER_URLS', '').split(',')
#         realm = 'realm1'
#         authentication = {
#             'cryptosign': {
#                 'privkey': '20e8c05d0ede9506462bb049c4843032b18e8e75b314583d0c8d8a4942f9be40',
#             }
#         }
#
#         component = Component(transports=transports, realm=realm, authentication=authentication)
#         # component.start()
#
#         # @inlineCallbacks
#         # def main(reactor, session):
#         #     print("Client session={}".format(session))
#         #     res = yield session.call('user.add2', 23, 666)
#         #     print(res)
#         #     session.leave()
#         #
#         # from autobahn.wamp.component import _run
#         # from twisted.internet import reactor
#         # d = _run(reactor, [component])
#         # #d = run([component], log_level='info', stop_at_close=True)
#         # res = yield d
