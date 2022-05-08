import os
import sys

from unittest import skipIf
from unittest.mock import MagicMock
from twisted.trial.unittest import TestCase

from twisted.internet.defer import inlineCallbacks

from autobahn.xbr import HAS_XBR
from autobahn.xbr._util import Datapool, Seeder

# https://web3py.readthedocs.io/en/stable/providers.html#infura-mainnet
HAS_INFURA = 'WEB3_INFURA_PROJECT_ID' in os.environ and len(os.environ['WEB3_INFURA_PROJECT_ID']) > 0

# TypeError: As of 3.10, the *loop* parameter was removed from Lock() since it is no longer necessary
IS_CPY_310 = sys.version_info.minor == 10


@skipIf(not HAS_XBR, 'package autobahn[xbr] not installed')
@skipIf(not HAS_INFURA, 'env var WEB3_INFURA_PROJECT_ID not defined')
class TestWeb3(TestCase):
    gw_config = {
        'type': 'infura',
        'key': os.environ.get('WEB3_INFURA_PROJECT_ID', ''),
        'network': 'mainnet',
    }

    # solved via websockets>=10.3, but web3==5.29.0 requires websockets<10
    @skipIf(IS_CPY_310, 'Web3 v5.29.0 (web3.auto.infura) raises TypeError on Python 3.10')
    def test_connect_w3_infura_auto(self):
        from web3.auto.infura import w3

        self.assertTrue(w3.isConnected())

    def test_connect_w3_autobahn(self):
        from autobahn.xbr import make_w3
        w3 = make_w3(self.gw_config)
        self.assertTrue(w3.isConnected())

    def test_ens_valid_names(self):
        from ens.main import ENS

        for name in ['wamp-proto.eth']:
            self.assertTrue(ENS.is_valid_name(name))

    def test_ens_resolve_names(self):
        from autobahn.xbr import make_w3
        from ens.main import ENS

        w3 = make_w3(self.gw_config)
        ens = ENS.fromWeb3(w3)
        for name, adr in [
            ('wamp-proto.eth', '0x66267d0b1114cFae80C37942177a846d666b114a'),
        ]:
            _adr = ens.address(name)
            self.assertEqual(adr, _adr)

    def test_datapool_ctor(self):
        name = 'wamp-proto.eth'

        dp1 = Datapool(name)
        self.assertEqual(dp1.status, 'STOPPED')
        self.assertEqual(dp1.name_or_address, name)
        self.assertEqual(dp1.gateway_config, None)
        self.assertEqual(dp1.name_category, 'ens')

        dp2 = Datapool(name, self.gw_config)
        self.assertEqual(dp2.status, 'STOPPED')
        self.assertEqual(dp2.name_or_address, name)
        self.assertEqual(dp2.gateway_config, self.gw_config)
        self.assertEqual(dp2.name_category, 'ens')

    @inlineCallbacks
    def test_datapool_initialize(self):
        name = 'wamp-proto.eth'

        dp1 = Datapool(name)

        self.assertEqual(dp1.status, 'STOPPED')
        yield dp1.initialize()
        self.assertEqual(dp1.status, 'RUNNING')

        self.assertEqual(dp1.address, '0x66267d0b1114cFae80C37942177a846d666b114a')

    def test_datapool_seeders(self):
        dp1 = MagicMock()
        dp1.name_or_address = 'wamp-proto.eth'
        dp1.address = '0x66267d0b1114cFae80C37942177a846d666b114a'
        dp1.status = 'RUNNING'
        dp1.seeders = [
            Seeder(url='wss://datapool1.example.com/ws',
                   label='Example Inc.',
                   operator='0xf5fb56886f033855C1a36F651E927551749361bC',
                   country='US'),
            Seeder(url='wss://dp1.foobar.org/ws',
                   label='Foobar Foundation',
                   operator='0xe59C7418403CF1D973485B36660728a5f4A8fF9c',
                   country='DE'),
            Seeder(url='wss://public-datapool1.pierre.fr:443',
                   label='Pierre PP',
                   operator='0x254dffcd3277C0b1660F6d42EFbB754edaBAbC2B',
                   country='FR'),
        ]
        self.assertEqual(len(dp1.seeders), 3)

        transports = [s.url for s in dp1.seeders]
        self.assertEqual(transports, ['wss://datapool1.example.com/ws', 'wss://dp1.foobar.org/ws',
                                      'wss://public-datapool1.pierre.fr:443'])
