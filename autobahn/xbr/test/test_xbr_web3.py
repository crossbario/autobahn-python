import os
import unittest
from autobahn.xbr import HAS_XBR

if HAS_XBR:
    from autobahn.xbr import make_w3
    from ens.main import ENS

# export WEB3_INFURA_PROJECT_ID="1c91697c211f4fcd8c7361f4c4e1f55f"
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
        for name in ['wamp-proto.eth']:
            self.assertTrue(ENS.is_valid_name(name))

    def test_ens_resolve_names(self):
        from web3.auto.infura import w3
        ens = ENS.fromWeb3(w3)
        for name, adr in [
            ('wamp-proto.eth', '0x66267d0b1114cFae80C37942177a846d666b114a'),
        ]:
            _adr = ens.address(name)
            self.assertEqual(adr, _adr)

# name = 'wamp-proto.eth'
#
# else:
#
# print('Is connected?', w3.isConnected())
#
# print('ENS name "{}" is valid?'.format(name), ENS.is_valid_name(name))
#
# adr = ens.address(name)
# print('Address is: {}'.format(adr))
# print('Address is checksummed?', w3.isChecksumAddress(adr))
#
# bal = w3.eth.get_balance(adr)
# print('Balance of address is: {} ETH'.format(w3.fromWei(bal, 'ether')))
#
# # WEB3_INFURA_PROJECT_ID="1c91697c211f4fcd8c7361f4c4e1f55f" time -f "%e" python -c "from web3.auto.infura import w3; print(w3.isConnected())"
# # web3.exceptions.InfuraKeyNotFound
