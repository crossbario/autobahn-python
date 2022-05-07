import os
import unittest
from autobahn.xbr import HAS_XBR

# https://web3py.readthedocs.io/en/stable/providers.html#infura-mainnet
HAS_INFURA = 'WEB3_INFURA_PROJECT_ID' in os.environ


@unittest.skipIf(not HAS_XBR, 'package autobahn[xbr] not installed')
@unittest.skipIf(not HAS_INFURA, 'env var WEB3_INFURA_PROJECT_ID not defined')
class TestWeb3(unittest.TestCase):

    def test_connect_w3_infura_auto(self):
        from web3.auto.infura import w3

        self.assertTrue(w3.isConnected())

    def test_connect_w3_autobahn(self):
        from autobahn.xbr import make_w3

        gw_config = {
            'type': 'infura',
            'key': os.environ['WEB3_INFURA_PROJECT_ID'],
            'network': 'mainnet',
        }
        w3 = make_w3(gw_config)
        self.assertTrue(w3.isConnected())

    def test_ens_valid_names(self):
        from ens.main import ENS

        for name in ['wamp-proto.eth']:
            self.assertTrue(ENS.is_valid_name(name))

    def test_ens_resolve_names(self):
        from web3.auto.infura import w3
        from ens.main import ENS

        ens = ENS.fromWeb3(w3)
        for name, adr in [
            ('wamp-proto.eth', '0x66267d0b1114cFae80C37942177a846d666b114a'),
        ]:
            _adr = ens.address(name)
            self.assertEqual(adr, _adr)
