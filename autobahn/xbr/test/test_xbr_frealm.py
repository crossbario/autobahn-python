import os
from unittest import skipIf
from unittest.mock import MagicMock
from twisted.trial.unittest import TestCase

from twisted.internet.defer import inlineCallbacks

from autobahn.xbr import HAS_XBR
if HAS_XBR:
    from autobahn.xbr._frealm import Seeder, FederatedRealm


@skipIf(not HAS_XBR, 'package autobahn[xbr] not installed')
class TestFederatedRealm(TestCase):

    gw_config = {
        'type': 'infura',
        'key': os.environ.get('WEB3_INFURA_PROJECT_ID', ''),
        'network': 'mainnet',
    }

    def test_frealm_ctor(self):
        name = 'wamp-proto.eth'

        fr1 = FederatedRealm(name)
        self.assertEqual(fr1.status, 'STOPPED')
        self.assertEqual(fr1.name_or_address, name)
        self.assertEqual(fr1.gateway_config, None)
        self.assertEqual(fr1.name_category, 'ens')

        fr2 = FederatedRealm(name, self.gw_config)
        self.assertEqual(fr2.status, 'STOPPED')
        self.assertEqual(fr2.name_or_address, name)
        self.assertEqual(fr2.gateway_config, self.gw_config)
        self.assertEqual(fr2.name_category, 'ens')

    @inlineCallbacks
    def test_frealm_initialize(self):
        name = 'wamp-proto.eth'
        fr1 = FederatedRealm(name)

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
