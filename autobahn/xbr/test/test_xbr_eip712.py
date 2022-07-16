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
from binascii import a2b_hex, b2a_hex
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
    from autobahn.xbr._eip712_delegate_certificate import EIP712DelegateCertificate

# https://web3py.readthedocs.io/en/stable/providers.html#infura-mainnet
HAS_INFURA = 'WEB3_INFURA_PROJECT_ID' in os.environ and len(os.environ['WEB3_INFURA_PROJECT_ID']) > 0

# TypeError: As of 3.10, the *loop* parameter was removed from Lock() since it is no longer necessary
IS_CPY_310 = sys.version_info.minor == 10


@skipIf(not os.environ.get('USE_TWISTED', False), 'only for Twisted')
@skipIf(not HAS_INFURA, 'env var WEB3_INFURA_PROJECT_ID not defined')
@skipIf(not (HAS_XBR and HAS_CRYPTOSIGN), 'package autobahn[encryption,xbr] not installed')
class TestEip712Certificate(TestCase):

    def setUp(self):
        self._gw_config = {
            'type': 'infura',
            'key': os.environ.get('WEB3_INFURA_PROJECT_ID', ''),
            'network': 'mainnet',
        }
        self._w3 = make_w3(self._gw_config)

        self._seedphrase = "avocado style uncover thrive same grace crunch want essay reduce current edge"
        self._sm: SecurityModuleMemory = SecurityModuleMemory.from_seedphrase(self._seedphrase, num_eth_keys=5,
                                                                              num_cs_keys=5)

    @inlineCallbacks
    def test_eip712_delegate_certificate(self):
        yield self._sm.open()

        delegate_eth_key: EthereumKey = self._sm[1]
        delegate_cs_key: CryptosignKey = self._sm[6]

        chainId = 1
        verifyingContract = a2b_hex('0xf766Dc789CF04CD18aE75af2c5fAf2DA6650Ff57'[2:])
        validFrom = 15124128
        delegate = delegate_eth_key.address(binary=True)
        csPubKey = delegate_cs_key.public_key(binary=True)
        bootedAt = 1657579546469365046  # txaio.time_ns()
        meta = 'Qme7ss3ARVgxv6rXqVPiikMJ8u2NLgmgszg13pYrDKEoiu'

        cert_data = create_eip712_delegate_certificate(chainId=chainId, verifyingContract=verifyingContract,
                                                       validFrom=validFrom, delegate=delegate, csPubKey=csPubKey,
                                                       bootedAt=bootedAt, meta=meta)

        # print('\n\n{}\n\n'.format(pformat(cert_data)))

        cert_sig = yield delegate_eth_key.sign_typed_data(cert_data, binary=False)

        self.assertEqual(cert_sig,
                         '2bd697b2bdb9bc2c2494e53e9440ddb3e8a596eedaad717f8ecdb732d091a7de48d72d9a26d7e092ec55c074979ab039f8e003acf80224819ff396c9529eb1d11b')

        yield self._sm.close()

    @inlineCallbacks
    def test_eip712_authority_certificate(self):
        yield self._sm.open()

        trustroot_eth_key: EthereumKey = self._sm[0]
        delegate_eth_key: EthereumKey = self._sm[1]

        chainId = 1
        verifyingContract = a2b_hex('0xf766Dc789CF04CD18aE75af2c5fAf2DA6650Ff57'[2:])
        validFrom = 15124128
        issuer = trustroot_eth_key.address(binary=True)
        subject = delegate_eth_key.address(binary=True)
        realm = a2b_hex('0xA6e693CC4A2b4F1400391a728D26369D9b82ef96'[2:])
        capabilities = 3
        meta = 'Qme7ss3ARVgxv6rXqVPiikMJ8u2NLgmgszg13pYrDKEoiu'

        cert_data = create_eip712_authority_certificate(chainId=chainId, verifyingContract=verifyingContract,
                                                        validFrom=validFrom, issuer=issuer, subject=subject,
                                                        realm=realm, capabilities=capabilities, meta=meta)

        # print('\n\n{}\n\n'.format(pformat(cert_data)))

        cert_sig = yield trustroot_eth_key.sign_typed_data(cert_data, binary=False)

        self.assertEqual(cert_sig,
                         '83590d4304cc5f6024d6a85ed2c511a60e804d609e4f498c8af777d5102c6d22657673e7b68876795e3c72f857b68e13cf616ee4c2ea559bceb344021bf977b61c')

        yield self._sm.close()


@skipIf(not os.environ.get('USE_TWISTED', False), 'only for Twisted')
@skipIf(not HAS_INFURA, 'env var WEB3_INFURA_PROJECT_ID not defined')
@skipIf(not (HAS_XBR and HAS_CRYPTOSIGN), 'package autobahn[encryption,xbr] not installed')
class TestEip712CertificateChain(TestCase):

    def setUp(self):
        self._gw_config = {
            'type': 'infura',
            'key': os.environ.get('WEB3_INFURA_PROJECT_ID', ''),
            'network': 'mainnet',
        }
        self._w3 = make_w3(self._gw_config)

        self._seedphrase = "avocado style uncover thrive same grace crunch want essay reduce current edge"
        self._sm: SecurityModuleMemory = SecurityModuleMemory.from_seedphrase(self._seedphrase, num_eth_keys=5,
                                                                              num_cs_keys=5)

        # HELLO.Details.authextra.certificates
        #
        self._certs_expected1 = [({'domain': {'name': 'WMP', 'version': '1'},
                                   'message': {'bootedAt': 1657781999086394759,
                                               'chainId': 1,
                                               'csPubKey': '12ae0184b180e9a9c5e45be4a1afbce3c6491320063701cd9c4011a777d04089',
                                               'delegate': '0xf5173a6111B2A6B3C20fceD53B2A8405EC142bF6',
                                               'meta': 'Qme7ss3ARVgxv6rXqVPiikMJ8u2NLgmgszg13pYrDKEoiu',
                                               'validFrom': 15139218,
                                               'verifyingContract': '0xf766Dc789CF04CD18aE75af2c5fAf2DA6650Ff57'},
                                   'primaryType': 'EIP712DelegateCertificate',
                                   'types': {'EIP712DelegateCertificate': [{'name': 'chainId',
                                                                            'type': 'uint256'},
                                                                           {'name': 'verifyingContract',
                                                                            'type': 'address'},
                                                                           {'name': 'validFrom',
                                                                            'type': 'uint256'},
                                                                           {'name': 'delegate',
                                                                            'type': 'address'},
                                                                           {'name': 'csPubKey',
                                                                            'type': 'bytes32'},
                                                                           {'name': 'bootedAt',
                                                                            'type': 'uint64'},
                                                                           {'name': 'meta', 'type': 'string'}],
                                             'EIP712Domain': [{'name': 'name', 'type': 'string'},
                                                              {'name': 'version', 'type': 'string'}]}},
                                  '70726dda677cac8f21366f8023d17203b2f4f9099e954f9bebb2134086e2ac291d80ce038a1342a7748d4b0750f06b8de491561d581c90c99f1c09c91cfa7e191c'),
                                 ({'domain': {'name': 'WMP', 'version': '1'},
                                   'message': {'capabilities': 3,
                                               'chainId': 1,
                                               'issuer': '0xf766Dc789CF04CD18aE75af2c5fAf2DA6650Ff57',
                                               'meta': 'QmNbMM6TMLAgqBKzY69mJKk5VKvpcTtAtwAaLC2FV4zC3G',
                                               'realm': '0xA6e693CC4A2b4F1400391a728D26369D9b82ef96',
                                               'subject': '0xf5173a6111B2A6B3C20fceD53B2A8405EC142bF6',
                                               'validFrom': 15139218,
                                               'verifyingContract': '0xf766Dc789CF04CD18aE75af2c5fAf2DA6650Ff57'},
                                   'primaryType': 'EIP712AuthorityCertificate',
                                   'types': {'EIP712AuthorityCertificate': [{'name': 'chainId',
                                                                             'type': 'uint256'},
                                                                            {'name': 'verifyingContract',
                                                                             'type': 'address'},
                                                                            {'name': 'validFrom',
                                                                             'type': 'uint256'},
                                                                            {'name': 'issuer',
                                                                             'type': 'address'},
                                                                            {'name': 'subject',
                                                                             'type': 'address'},
                                                                            {'name': 'realm',
                                                                             'type': 'address'},
                                                                            {'name': 'capabilities',
                                                                             'type': 'uint64'},
                                                                            {'name': 'meta', 'type': 'string'}],
                                             'EIP712Domain': [{'name': 'name', 'type': 'string'},
                                                              {'name': 'version', 'type': 'string'}]}},
                                  'd625b069771de42f7ef81680219c037f7037a43ee5692efea03764ab361438fc3777346455d20c09f13cd5bae1d992c122095a2ae261130edabf58a7900d661b1b')]

    @inlineCallbacks
    def test_eip712_create_certificate_chain(self):
        yield self._sm.open()

        # keys needed to create all certificates in certificate chain
        #
        trustroot_eth_key: EthereumKey = self._sm[0]
        delegate_eth_key: EthereumKey = self._sm[1]
        delegate_cs_key: CryptosignKey = self._sm[6]

        # data needed for delegate certificate
        #
        chainId = 1  # self._w3.eth.chain_id
        verifyingContract = a2b_hex('0xf766Dc789CF04CD18aE75af2c5fAf2DA6650Ff57'[2:])
        validFrom = 15139218  # self._w3.eth.block_number
        delegate = delegate_eth_key.address(binary=True)
        csPubKey = delegate_cs_key.public_key(binary=True)
        bootedAt = 1657781999086394759  # txaio.time_ns()
        delegateMeta = 'Qme7ss3ARVgxv6rXqVPiikMJ8u2NLgmgszg13pYrDKEoiu'

        # data needed for authority certificate
        #
        issuer = trustroot_eth_key.address(binary=True)
        subject = delegate
        realm = a2b_hex('0xA6e693CC4A2b4F1400391a728D26369D9b82ef96'[2:])
        capabilities = 3
        authorityMeta = 'QmNbMM6TMLAgqBKzY69mJKk5VKvpcTtAtwAaLC2FV4zC3G'

        # create delegate certificate
        #
        cert1_data = create_eip712_delegate_certificate(chainId=chainId, verifyingContract=verifyingContract,
                                                        validFrom=validFrom, delegate=delegate, csPubKey=csPubKey,
                                                        bootedAt=bootedAt, meta=delegateMeta)

        cert1_sig = yield delegate_eth_key.sign_typed_data(cert1_data, binary=False)

        cert1_data['message']['csPubKey'] = b2a_hex(cert1_data['message']['csPubKey']).decode()
        cert1_data['message']['delegate'] = self._w3.toChecksumAddress(cert1_data['message']['delegate'])
        cert1_data['message']['verifyingContract'] = self._w3.toChecksumAddress(
            cert1_data['message']['verifyingContract'])

        # create authority certificate
        #
        cert2_data = create_eip712_authority_certificate(chainId=chainId, verifyingContract=verifyingContract,
                                                         validFrom=validFrom, issuer=issuer, subject=subject,
                                                         realm=realm, capabilities=capabilities, meta=authorityMeta)

        cert2_sig = yield trustroot_eth_key.sign_typed_data(cert2_data, binary=False)

        cert2_data['message']['verifyingContract'] = self._w3.toChecksumAddress(
            cert2_data['message']['verifyingContract'])
        cert2_data['message']['issuer'] = self._w3.toChecksumAddress(cert2_data['message']['issuer'])
        cert2_data['message']['subject'] = self._w3.toChecksumAddress(cert2_data['message']['subject'])
        cert2_data['message']['realm'] = self._w3.toChecksumAddress(cert2_data['message']['realm'])

        # create certificates chain
        #
        certificates = [(cert1_data, cert1_sig), (cert2_data, cert2_sig)]

        self.assertEqual(cert1_sig,
                         '70726dda677cac8f21366f8023d17203b2f4f9099e954f9bebb2134086e2ac291d80ce038a1342a7748d4b0750f06b8de491561d581c90c99f1c09c91cfa7e191c')
        self.assertEqual(cert2_sig,
                         'd625b069771de42f7ef81680219c037f7037a43ee5692efea03764ab361438fc3777346455d20c09f13cd5bae1d992c122095a2ae261130edabf58a7900d661b1b')

        self.assertEqual(certificates, self._certs_expected1)

        yield self._sm.close()

    @inlineCallbacks
    def test_eip712_verify_certificate_chain(self):
        yield self._sm.open()

        # keys needed to create all certificates in certificate chain
        #
        # trustroot_eth_key: EthereumKey = self._sm[0]
        # delegate_eth_key: EthereumKey = self._sm[1]
        # delegate_cs_key: CryptosignKey = self._sm[6]

        for cert_data, cert_sig in self._certs_expected1:
            self.assertIn('domain', cert_data)
            self.assertIn('message', cert_data)
            self.assertIn('primaryType', cert_data)
            self.assertIn('types', cert_data)
            self.assertIn(cert_data['primaryType'], cert_data['types'])

            self.assertIn(cert_data['primaryType'], ['EIP712DelegateCertificate', 'EIP712AuthorityCertificate'])

            if cert_data['primaryType'] == 'EIP712DelegateCertificate':
                EIP712DelegateCertificate.parse(cert_data['message'])

        yield self._sm.close()
