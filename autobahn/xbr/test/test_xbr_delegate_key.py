import os
import sys
from binascii import a2b_hex
from unittest import skipIf

from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase

from py_eth_sig_utils.eip712 import encode_typed_data
from py_eth_sig_utils.utils import ecsign
from py_eth_sig_utils.signing import v_r_s_to_signature
from py_eth_sig_utils.signing import sign_typed_data

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

        self._seedphrase = "avocado style uncover thrive same grace crunch want essay reduce current edge"
        self._addresses = [
            '0xf766Dc789CF04CD18aE75af2c5fAf2DA6650Ff57',
            '0xf5173a6111B2A6B3C20fceD53B2A8405EC142bF6',
            '0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047',
            '0x2F070c2f49a59159A0346396f1139203355ACA43',
            '0x66290fA8ADcD901Fd994e4f64Cfb53F4c359a326',
            '0xAA8Cc377db31a354137d8Bb86D0E38495dbD5266',
            '0xeD22Fd82230B613a638e09E90dfBFeE6d604D3D2',
            '0xfe79337902575cFF28f6c7B34ff718149fcC4849',
            '0x8337Cd9Ec2e0aB3370DF3AA6D4cc29614ec9dDe4',
            '0x29B6c56497CA179e9AAFD739BeBded3f23768903',
            '0x163D58cE482560B7826b4612f40aa2A7d53310C4',
            '0x72b3486d38E9f49215b487CeAaDF27D6acf22115',
            '0x52d66f36A7927cF9612e1b40bD6549d08E0513Ff',
            '0xFfa4F46DD8f537F3E73c4A8e056948856fa79Bf0',
            '0x6231eECbA6e7983efe5ce6d16972E16cCcD97CE7',
            '0x5f61F4c611501c1084738c0c8c5EbB5D3d8f2B6E',
            '0xA6e693CC4A2b4F1400391a728D26369D9b82ef96',
            '0xE51007F2bB31604Ddd531d0B48f8bFf5703755A8',
            '0x60CC48BFC44b48A53e793FE4cB50e2d625BABB27',
            '0xe78ea2fE1533D4beD9A10d91934e109A130D0ad8',
        ]
        self._keys = [
            '0x805f84af7e182359db0610ffb07c801012b699b5610646937704aa5cfc28b15e',
            '0x991c8f7609f3236ad5ef6d498b2ec0c9793c2865dd337ddc3033067c1da0e735',
            '0x75848ddb1155cd1cdf6d74a6e7fbed06aeaa21ef2d8a05df7af2d95cdc127672',
            '0x5be599a34927a1110922d7704ba316144b31699d8e7f229e2684d5575a84214e',
            '0xc1bb7ce3481e95b28bb8c026667b6009c504c79a98e6c7237ba0788c37b473c9',
            '0xbd7f02a1ca01492bfe63472adf185a5822a6bcd9686818b98e4da9dec87243cc',
            '0x15d03ceae8d93dbdda6301385abc9e0ca07162671e20ce2133de712dbb30a5f0',
            '0xbe32f0d4b6c5a8e03e68f5fa9dd755f572b77031ec8287f73366ad7ca18eafbe',
            '0xd13669786f8e021a379ef4708b5ad538e5eb2305d36e05f93e08c95ae8af2a64',
            '0xc14deab4c696362123a6792f5aa1b230fd552d5ae60eccb2e5b0c0bedc134fc1',
            '0xc9b518d9cac2d2e3888bf430afcd3561d7b10bb14ffa85a87d445e206d7f7552',
            '0x7fbbdc86c7c7d18e3778e4f0a067fa8f86963610fc9a103df53fc1d65bc052d1',
            '0xc83702a545384c259da8542ae0184f9654dcfdb2025f6165c0b81c6e04b4c212',
            '0x6c7ff5b6daccf5054d436733188f6147ab7b674bf7abc7c7feba0a9a70ec42e4',
            '0x04139894d1f465fcaf295ec18044fb2eaaf9fcc7bf51190f816800fd7eab3479',
            '0x521cbf9e86501aeb1bce0095eba6d234c16b9494aa2493fcb821c9d2b7c88cbc',
            '0xe12ff0b82c9206b8c2c218e3f63fe94e6712c469da48a91aa192dacbb8cb75a5',
            '0x60c2661dac98eb99b7dd6bd4f6a547ef105d0ed2879cf301f412267768cac56a',
            '0xbdb81319735d3872e4a207c3b16a08fc7f963a34e0e178f5b85314c15dc24163',
            '0x41e33a4387b4546a80839e2dafae469a08a59676244de08d012cf1f8d0f47e89',
        ]

        # create EIP712 typed data dict from message data
        verifying_contract = a2b_hex('0x2F070c2f49a59159A0346396f1139203355ACA43'[2:])
        member = a2b_hex('0xA6e693CC4A2b4F1400391a728D26369D9b82ef96'[2:])
        eula = 'QmU7Gizbre17x6V2VR1Q2GJEjz6m8S1bXmBtVxS2vmvb81'
        profile = 'QmcNsPV7QZFHKb2DNn8GWsU5dtd8zH5DNRa31geC63ceb4'
        self._eip_data_objects = [
            _create_eip712_member_register(chainId=1, verifyingContract=verifying_contract, member=member,
                                           registered=666, eula=eula, profile=profile),
        ]

    def test_from_seedphrase(self):
        for i in range(len(self._keys)):
            key = EthereumKey.from_seedphrase(self._seedphrase, i)
            self.assertEqual(key.address(binary=False), self._addresses[i])

    def test_from_bytes(self):
        for i in range(len(self._keys)):
            key_raw = a2b_hex(self._keys[i][2:])
            key = EthereumKey.from_bytes(key_raw)
            self.assertEqual(key.address(binary=False), self._addresses[i])
            self.assertEqual(key._key.key, key_raw)

    @inlineCallbacks
    def test_sign_typed_data(self):
        key_raw = a2b_hex(self._keys[0][2:])

        # 1. py_eth_sig_utils: test by doing individual steps / manually
        data = self._eip_data_objects[0]

        # encode typed data dict and return message hash
        msg_hash = encode_typed_data(data)
        self.assertEqual(msg_hash, a2b_hex('e7e354cc11e83970374ab27c6a37282139ee7b531d7d5e291532c842e44035b4'))

        # sign message hash with private key
        signature_vrs = ecsign(msg_hash, key_raw)
        self.assertEqual(signature_vrs, (27, 26144801574096978964301126643765838249150105757723589274956631127014141376315, 9140535639818377710828404916067108362243171873197203693677839588603381703230))

        # concatenate signature components into byte string
        signature = v_r_s_to_signature(*signature_vrs)

        # ECDSA signatures in Ethereum consist of three parameters: v, r and s.
        # The signature is always 65-bytes in length.
        #     r = first 32 bytes of signature
        #     s = second 32 bytes of signature
        #     v = final 1 byte of signature
        self.assertEqual(len(signature), 65)
        self.assertEqual(signature, a2b_hex('39cd6eec124908a9da2e42ff1e93baf97ad8a08865d60f5f00cdd0c233bcb73b14355c1e286d630be6f012c485f11b684adc6725fc010dd669f8131fb39c623e1b'))

        # 2. py_eth_sig_utils: test using high level function

        signature_vrs_2 = sign_typed_data(data, key_raw)

        self.assertEqual(signature_vrs_2, signature_vrs)

        # 3. EthereumKey: test using autobahn async function

        key = EthereumKey.from_bytes(key_raw)
        signature_3 = yield key.sign_typed_data(data)
        self.assertEqual(signature_3, signature)

    def test_verify_typed_data(self):
        pass
