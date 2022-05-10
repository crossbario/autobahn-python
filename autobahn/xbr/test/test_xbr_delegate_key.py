import os
import sys
from binascii import a2b_hex
from unittest import skipIf

from twisted.trial.unittest import TestCase

from py_eth_sig_utils.eip712 import encode_typed_data
from py_eth_sig_utils.utils import ecsign
from py_eth_sig_utils.signing import v_r_s_to_signature
# from py_eth_sig_utils.signing import sign_typed_data

from autobahn.xbr import HAS_XBR
from autobahn.xbr import make_w3, EthereumKey
from autobahn.xbr._eip712_member_register import _create_eip712_member_register


# https://web3py.readthedocs.io/en/stable/providers.html#infura-mainnet
HAS_INFURA = 'WEB3_INFURA_PROJECT_ID' in os.environ and len(os.environ['WEB3_INFURA_PROJECT_ID']) > 0

# TypeError: As of 3.10, the *loop* parameter was removed from Lock() since it is no longer necessary
IS_CPY_310 = sys.version_info.minor == 10


@skipIf(not os.environ.get('USE_TWISTED', False), 'only for Twisted')
@skipIf(not HAS_INFURA, 'env var WEB3_INFURA_PROJECT_ID not defined')
@skipIf(not HAS_XBR, 'package autobahn[xbr] not installed')
class TestEthereumKey(TestCase):

    def setUp(self):
        self._gw_config = {
            'type': 'infura',
            'key': os.environ.get('WEB3_INFURA_PROJECT_ID', ''),
            'network': 'mainnet',
        }
        self._w3 = make_w3(self._gw_config)

    def test_from_seedphrase(self):
        seedphrase = "myth like bonus scare over problem client lizard pioneer submit female collect"
        key = EthereumKey.from_seedphrase(seedphrase, 0)
        self.assertEqual(key.address(binary=False), '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1')

    def test_from_bytes(self):
        seed = a2b_hex('0x805f84af7e182359db0610ffb07c801012b699b5610646937704aa5cfc28b15e'[2:])
        key = EthereumKey.from_bytes(seed)
        self.assertEqual(key.address(binary=False), '0xf766Dc789CF04CD18aE75af2c5fAf2DA6650Ff57')
        self.assertEqual(key._key.key, seed)

    def test_sign_typed_data(self):
        private_key = a2b_hex('0x805f84af7e182359db0610ffb07c801012b699b5610646937704aa5cfc28b15e'[2:])

        # message data to sign
        chain_id = 1
        verifying_contract = a2b_hex('0x2F070c2f49a59159A0346396f1139203355ACA43'[2:])
        member = a2b_hex('0xA6e693CC4A2b4F1400391a728D26369D9b82ef96'[2:])
        registered = 666
        eula = 'QmU7Gizbre17x6V2VR1Q2GJEjz6m8S1bXmBtVxS2vmvb81'
        profile = 'QmcNsPV7QZFHKb2DNn8GWsU5dtd8zH5DNRa31geC63ceb4'

        # create EIP712 typed data dict from message data
        data = _create_eip712_member_register(chainId=chain_id, verifyingContract=verifying_contract, member=member,
                                              registered=registered, eula=eula, profile=profile)

        # encode typed data dict and return message hash
        msg_hash = encode_typed_data(data)
        self.assertEqual(msg_hash, a2b_hex('e7e354cc11e83970374ab27c6a37282139ee7b531d7d5e291532c842e44035b4'))

        # sign message hash with private key
        signature_vrs = ecsign(msg_hash, private_key)
        self.assertEqual(signature_vrs, (27, 26144801574096978964301126643765838249150105757723589274956631127014141376315, 9140535639818377710828404916067108362243171873197203693677839588603381703230))

        # concatenate signature components into byte string
        signature = v_r_s_to_signature(*signature_vrs)
        self.assertEqual(signature, a2b_hex('39cd6eec124908a9da2e42ff1e93baf97ad8a08865d60f5f00cdd0c233bcb73b14355c1e286d630be6f012c485f11b684adc6725fc010dd669f8131fb39c623e1b'))
