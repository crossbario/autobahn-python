import os
import sys

from unittest import skipIf
from twisted.trial.unittest import TestCase

from autobahn.xbr import HAS_XBR

# https://web3py.readthedocs.io/en/stable/providers.html#infura-mainnet
HAS_INFURA = 'WEB3_INFURA_PROJECT_ID' in os.environ and len(os.environ['WEB3_INFURA_PROJECT_ID']) > 0

# TypeError: As of 3.10, the *loop* parameter was removed from Lock() since it is no longer necessary
IS_CPY_310 = sys.version_info.minor >= 10


@skipIf(not HAS_XBR, 'package autobahn[xbr] not installed')
@skipIf(not HAS_INFURA, 'env var WEB3_INFURA_PROJECT_ID not defined')
class TestWeb3(TestCase):
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
    @skipIf(True, 'FIXME: web3.auto.infura was removed')
    def test_connect_w3_infura_auto(self):
        from web3.auto.infura import w3

        self.assertTrue(w3.isConnected())

    def test_connect_w3_autobahn(self):
        from autobahn.xbr import make_w3
        w3 = make_w3(self.gw_config)
        self.assertTrue(w3.isConnected())

    def test_ens_valid_names(self):
        from ens.ens import ENS

        for name in ['wamp-proto.eth']:
            self.assertTrue(ENS.is_valid_name(name))

    def test_ens_resolve_names(self):
        from autobahn.xbr import make_w3
        from ens.ens import ENS

        w3 = make_w3(self.gw_config)
        ens = ENS.from_web3(w3)
        for name, adr in [
            ('wamp-proto.eth', '0x66267d0b1114cFae80C37942177a846d666b114a'),
        ]:
            _adr = ens.address(name)
            self.assertEqual(adr, _adr)
