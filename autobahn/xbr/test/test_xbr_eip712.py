###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

import os
import sys
from binascii import a2b_hex
from pprint import pformat
from unittest import skipIf

from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase

from autobahn.wamp.cryptosign import HAS_CRYPTOSIGN
from autobahn.xbr import HAS_XBR

if HAS_XBR and HAS_CRYPTOSIGN:
    from autobahn.wamp.cryptosign import CryptosignKey
    from autobahn.xbr import make_w3, EthereumKey
    from autobahn.xbr._secmod import SecurityModuleMemory
    from autobahn.xbr import create_eip712_delegate_certificate, create_eip712_authority_certificate


# https://web3py.readthedocs.io/en/stable/providers.html#infura-mainnet
HAS_INFURA = 'WEB3_INFURA_PROJECT_ID' in os.environ and len(os.environ['WEB3_INFURA_PROJECT_ID']) > 0

# TypeError: As of 3.10, the *loop* parameter was removed from Lock() since it is no longer necessary
IS_CPY_310 = sys.version_info.minor == 10


@skipIf(not os.environ.get('USE_TWISTED', False), 'only for Twisted')
@skipIf(not HAS_INFURA, 'env var WEB3_INFURA_PROJECT_ID not defined')
@skipIf(not (HAS_XBR and HAS_CRYPTOSIGN), 'package autobahn[encryption,xbr] not installed')
class TestEip712(TestCase):

    def setUp(self):
        self._gw_config = {
            'type': 'infura',
            'key': os.environ.get('WEB3_INFURA_PROJECT_ID', ''),
            'network': 'mainnet',
        }
        self._w3 = make_w3(self._gw_config)

        self._seedphrase = "avocado style uncover thrive same grace crunch want essay reduce current edge"
        self._sm: SecurityModuleMemory = SecurityModuleMemory.from_seedphrase(self._seedphrase, num_eth_keys=5, num_cs_keys=5)

    @inlineCallbacks
    def test_eip712_delegate_certificate(self):
        yield self._sm.open()

        delegate_eth_key: EthereumKey = self._sm[1]
        delegate_cs_key: CryptosignKey = self._sm[6]

        chainId = 1
        validFrom = 1
        verifyingContract = a2b_hex('0xf766Dc789CF04CD18aE75af2c5fAf2DA6650Ff57'[2:])
        delegate = delegate_eth_key.address(binary=True)
        csPubKey = delegate_cs_key.public_key(binary=True)
        csChallenge = a2b_hex('eb870538efe96311e4cd9b18947bbff491d5d31a7b292c5b6ca48f6ad24f16dd')
        csChannelId = a2b_hex('70f1c7ecaf43858f256d45c4c5db76a2b1b2c18c418fc828600f1ce9e1f71ce1')
        reservation = a2b_hex('0xe78ea2fE1533D4beD9A10d91934e109A130D0ad8'[2:])

        cert_data = create_eip712_delegate_certificate(chainId=chainId, verifyingContract=verifyingContract,
                                                       validFrom=validFrom, delegate=delegate, csPubKey=csPubKey,
                                                       csChallenge=csChallenge, csChannelId=csChannelId,
                                                       reservation=reservation)

        print('\n\n{}\n\n'.format(pformat(cert_data)))

        cert_sig = yield delegate_eth_key.sign_typed_data(cert_data, binary=False)

        self.assertEqual(cert_sig, 'd716910a8c4cd3a10c200d332cffcbc1f143adea429c67f01e72b43ddc8a9676158ae2b1d64f4ffbddf4da91635f5ae90ac4d1975339da20bb1dd50e39a0c7ce1b')

        yield self._sm.close()

    @inlineCallbacks
    def test_eip712_authority_certificate(self):
        yield self._sm.open()

        trustroot_eth_key: EthereumKey = self._sm[0]
        delegate_eth_key: EthereumKey = self._sm[1]

        chainId = 1
        validFrom = 1
        verifyingContract = a2b_hex('0xf766Dc789CF04CD18aE75af2c5fAf2DA6650Ff57'[2:])
        authority = a2b_hex('0xe78ea2fE1533D4beD9A10d91934e109A130D0ad8'[2:])
        delegate = delegate_eth_key.address(binary=True)
        domain = a2b_hex('0x5f61F4c611501c1084738c0c8c5EbB5D3d8f2B6E'[2:])
        realm = a2b_hex('0xA6e693CC4A2b4F1400391a728D26369D9b82ef96'[2:])
        role = 'consumer'

        cert_data = create_eip712_authority_certificate(chainId=chainId, verifyingContract=verifyingContract,
                                                        validFrom=validFrom, authority=authority, delegate=delegate,
                                                        domain=domain, realm=realm, role=role)

        print('\n\n{}\n\n'.format(pformat(cert_data)))

        cert_sig = yield trustroot_eth_key.sign_typed_data(cert_data, binary=False)

        self.assertEqual(cert_sig, 'ce873125c294936a5fdb86cbbc94613e3b92010df2c915360493b5aace5f571335f53ab181d0d243e0b8882c0eb2400f2aa63c80774cdfc9dc6d4653296c93061b')

        yield self._sm.close()
