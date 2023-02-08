###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
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
import tempfile
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
    from autobahn.xbr._eip712_authority_certificate import EIP712AuthorityCertificate
    from autobahn.xbr._eip712_certificate_chain import parse_certificate_chain

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
        self._certs_expected1 = [(None,
                                  {'domain': {'name': 'WMP', 'version': '1'},
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
                                 (None,
                                  {'domain': {'name': 'WMP', 'version': '1'},
                                   'message': {'capabilities': 12,
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
                                  'f031b2625ae7e32e7eec3a8fa09f4db3a43217f282b7695e5b09dd2e13c25dc679c1f3ce27b94a3074786f7f12183a2a275a00aea5a66b83c431281f1069bd841c'),
                                 (None,
                                  {'domain': {'name': 'WMP', 'version': '1'},
                                   'message': {'capabilities': 63,
                                               'chainId': 1,
                                               'issuer': '0xf766Dc789CF04CD18aE75af2c5fAf2DA6650Ff57',
                                               'meta': 'QmNbMM6TMLAgqBKzY69mJKk5VKvpcTtAtwAaLC2FV4zC3G',
                                               'realm': '0xA6e693CC4A2b4F1400391a728D26369D9b82ef96',
                                               'subject': '0xf766Dc789CF04CD18aE75af2c5fAf2DA6650Ff57',
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
                                  'c3bcd7a3c3c45ae45a24cd7745db3b39c4113e6b71a4220f943f0969282246b4083ef61277bd7ba9e92c9a07b79869ce63bc6206986480f9c5daddb27b91bebe1b')]

    @skipIf(True, 'FIXME: builtins.TypeError: to_checksum_address() takes 1 positional argument but 2 were given')
    @inlineCallbacks
    def test_eip712_create_certificate_chain_manual(self):
        yield self._sm.open()

        # keys needed to create all certificates in certificate chain
        #
        trustroot_eth_key: EthereumKey = self._sm[0]
        delegate_eth_key: EthereumKey = self._sm[1]
        delegate_cs_key: CryptosignKey = self._sm[6]

        # data needed for delegate certificate: cert1
        #
        chainId = 1  # self._w3.eth.chain_id
        verifyingContract = a2b_hex('0xf766Dc789CF04CD18aE75af2c5fAf2DA6650Ff57'[2:])
        validFrom = 15139218  # self._w3.eth.block_number
        delegate = delegate_eth_key.address(binary=True)
        csPubKey = delegate_cs_key.public_key(binary=True)
        bootedAt = 1657781999086394759  # txaio.time_ns()
        delegateMeta = 'Qme7ss3ARVgxv6rXqVPiikMJ8u2NLgmgszg13pYrDKEoiu'

        # data needed for intermediate authority certificate: cert2
        #
        issuer_cert2 = trustroot_eth_key.address(binary=True)
        subject_cert2 = delegate
        realm_cert2 = a2b_hex('0xA6e693CC4A2b4F1400391a728D26369D9b82ef96'[2:])
        capabilities_cert2 = EIP712AuthorityCertificate.CAPABILITY_PUBLIC_RELAY | EIP712AuthorityCertificate.CAPABILITY_PRIVATE_RELAY
        meta_cert2 = 'QmNbMM6TMLAgqBKzY69mJKk5VKvpcTtAtwAaLC2FV4zC3G'

        # data needed for root authority certificate: cert3
        #
        issuer_cert3 = trustroot_eth_key.address(binary=True)
        subject_cert3 = issuer_cert3
        realm_cert3 = a2b_hex('0xA6e693CC4A2b4F1400391a728D26369D9b82ef96'[2:])
        capabilities_cert3 = EIP712AuthorityCertificate.CAPABILITY_ROOT_CA | EIP712AuthorityCertificate.CAPABILITY_INTERMEDIATE_CA | EIP712AuthorityCertificate.CAPABILITY_PUBLIC_RELAY | EIP712AuthorityCertificate.CAPABILITY_PRIVATE_RELAY | EIP712AuthorityCertificate.CAPABILITY_PROVIDER | EIP712AuthorityCertificate.CAPABILITY_CONSUMER
        meta_cert3 = 'QmNbMM6TMLAgqBKzY69mJKk5VKvpcTtAtwAaLC2FV4zC3G'

        # FIXME: builtins.TypeError: to_checksum_address() takes 1 positional argument but 2 were given

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

        # create intermediate authority certificate
        #
        cert2_data = create_eip712_authority_certificate(chainId=chainId, verifyingContract=verifyingContract,
                                                         validFrom=validFrom, issuer=issuer_cert2,
                                                         subject=subject_cert2,
                                                         realm=realm_cert2, capabilities=capabilities_cert2,
                                                         meta=meta_cert2)

        cert2_sig = yield trustroot_eth_key.sign_typed_data(cert2_data, binary=False)

        cert2_data['message']['verifyingContract'] = self._w3.toChecksumAddress(
            cert2_data['message']['verifyingContract'])
        cert2_data['message']['issuer'] = self._w3.toChecksumAddress(cert2_data['message']['issuer'])
        cert2_data['message']['subject'] = self._w3.toChecksumAddress(cert2_data['message']['subject'])
        cert2_data['message']['realm'] = self._w3.toChecksumAddress(cert2_data['message']['realm'])

        # create root authority certificate
        #
        cert3_data = create_eip712_authority_certificate(chainId=chainId, verifyingContract=verifyingContract,
                                                         validFrom=validFrom, issuer=issuer_cert3,
                                                         subject=subject_cert3,
                                                         realm=realm_cert3, capabilities=capabilities_cert3,
                                                         meta=meta_cert3)

        cert3_sig = yield trustroot_eth_key.sign_typed_data(cert3_data, binary=False)

        cert3_data['message']['verifyingContract'] = self._w3.toChecksumAddress(
            cert3_data['message']['verifyingContract'])
        cert3_data['message']['issuer'] = self._w3.toChecksumAddress(cert3_data['message']['issuer'])
        cert3_data['message']['subject'] = self._w3.toChecksumAddress(cert3_data['message']['subject'])
        cert3_data['message']['realm'] = self._w3.toChecksumAddress(cert3_data['message']['realm'])

        # create certificates chain
        #
        certificates = [(None, cert1_data, cert1_sig), (None, cert2_data, cert2_sig), (None, cert3_data, cert3_sig)]

        if False:
            from pprint import pprint
            print()
            pprint(certificates)
            print()

        # check certificates and certificate signatures of whole chain
        #
        self.assertEqual(certificates, self._certs_expected1)

        yield self._sm.close()

    @inlineCallbacks
    def test_eip712_create_certificate_chain_highlevel(self):
        yield self._sm.open()

        # keys needed to create all certificates in certificate chain
        ca_key: EthereumKey = self._sm[0]

        # data needed for root authority certificate: cert3
        ca_cert_chainId = 1
        ca_cert_verifyingContract = a2b_hex('0xf766Dc789CF04CD18aE75af2c5fAf2DA6650Ff57'[2:])
        ca_cert_validFrom = 666666
        ca_cert_issuer = ca_key.address(binary=True)
        ca_cert_subject = ca_cert_issuer
        ca_cert_realm = a2b_hex('0xA6e693CC4A2b4F1400391a728D26369D9b82ef96'[2:])
        ca_cert_capabilities = EIP712AuthorityCertificate.CAPABILITY_ROOT_CA | EIP712AuthorityCertificate.CAPABILITY_INTERMEDIATE_CA | EIP712AuthorityCertificate.CAPABILITY_PUBLIC_RELAY | EIP712AuthorityCertificate.CAPABILITY_PRIVATE_RELAY | EIP712AuthorityCertificate.CAPABILITY_PROVIDER | EIP712AuthorityCertificate.CAPABILITY_CONSUMER
        ca_cert_meta = ''

        # create root authority certificate signature: directly from provided data attributes
        ca_cert_data = create_eip712_authority_certificate(chainId=ca_cert_chainId,
                                                           verifyingContract=ca_cert_verifyingContract,
                                                           validFrom=ca_cert_validFrom, issuer=ca_cert_issuer,
                                                           subject=ca_cert_subject, realm=ca_cert_realm,
                                                           capabilities=ca_cert_capabilities, meta=ca_cert_meta)
        ca_cert_sig = yield ca_key.sign_typed_data(ca_cert_data, binary=False)

        # create root authority certificate signature: from certificate object
        ca_cert = EIP712AuthorityCertificate(chainId=ca_cert_chainId,
                                             verifyingContract=ca_cert_verifyingContract,
                                             validFrom=ca_cert_validFrom,
                                             issuer=ca_cert_issuer,
                                             subject=ca_cert_subject,
                                             realm=ca_cert_realm,
                                             capabilities=ca_cert_capabilities,
                                             meta=ca_cert_meta)
        ca_cert_sig2 = yield ca_cert.sign(ca_key)

        # re-create root authority certificate from round-tripping (marshal-parse)
        ca_cert2 = EIP712AuthorityCertificate.parse(ca_cert.marshal())
        ca_cert_sig3 = yield ca_cert2.sign(ca_key)

        # all different ways to compute signature must result in same signature value
        self.assertEqual(ca_cert_sig, ca_cert_sig2)
        self.assertEqual(ca_cert_sig, ca_cert_sig3)

        # and match this signature value
        self.assertEqual(ca_cert_sig, 'd9e679753e1120a8ba8edea4895d2e056ba98eaa1acbe11bf6210f3a48a56de830aa6a566cc4920'
                                      'c74a284ffcd9f7d1af5fe229268a44030522db19d5a75f4131c')

        # test save/load instance to/from file
        with tempfile.NamedTemporaryFile() as fd:
            # save certificate to file
            ca_cert.save(fd.name)

            # load certificate from file
            ca_cert3 = EIP712AuthorityCertificate.load(fd.name)

            # ensure it produces the same signature
            ca_cert_sig4 = yield ca_cert3.sign(ca_key)
            self.assertEqual(ca_cert_sig, ca_cert_sig4)

        yield self._sm.close()

    @inlineCallbacks
    def test_eip712_verify_certificate_chain_manual(self):
        yield self._sm.open()

        # keys originally used to sign the certificates in the certificate chain
        trustroot_eth_key: EthereumKey = self._sm[0]
        delegate_eth_key: EthereumKey = self._sm[1]
        delegate_cs_key: CryptosignKey = self._sm[6]

        # parse the whole certificate chain
        cert_chain = []
        cert_sigs = []
        for cert_hash, cert_data, cert_sig in self._certs_expected1:
            self.assertIn('domain', cert_data)
            self.assertIn('message', cert_data)
            self.assertIn('primaryType', cert_data)
            self.assertIn('types', cert_data)
            self.assertIn(cert_data['primaryType'], cert_data['types'])
            self.assertIn(cert_data['primaryType'], ['EIP712DelegateCertificate', 'EIP712AuthorityCertificate'])
            if cert_data['primaryType'] == 'EIP712DelegateCertificate':
                cert = EIP712DelegateCertificate.parse(cert_data)
            elif cert_data['primaryType'] == 'EIP712AuthorityCertificate':
                cert = EIP712AuthorityCertificate.parse(cert_data)
            else:
                assert False, 'should not arrive here'
            cert_chain.append(cert)
            cert_sigs.append(cert_sig)

        # FIXME: allow length 2 and length > 3
        self.assertEqual(len(cert_chain), 3)
        self.assertEqual(cert_chain[0].delegate, delegate_eth_key.address(binary=True))
        self.assertEqual(cert_chain[0].csPubKey, delegate_cs_key.public_key(binary=True))
        self.assertEqual(cert_chain[1].issuer, trustroot_eth_key.address(binary=True))
        self.assertEqual(cert_chain[2].issuer, trustroot_eth_key.address(binary=True))

        # Certificate Chain Rules (CCR):
        #
        # 1. **CCR-1**: The `chainId` and `verifyingContract` must match for all certificates to what we expect, and `validFrom` before current block number on the respective chain.
        # 2. **CCR-2**: The `realm` must match for all certificates to the respective realm.
        # 3. **CCR-3**: The type of the first certificate in the chain must be a `EIP712DelegateCertificate`, and all subsequent certificates must be of type `EIP712AuthorityCertificate`.
        # 4. **CCR-4**: The last certificate must be self-signed (`issuer` equals `subject`), it is a root CA certificate.
        # 5. **CCR-5**: The intermediate certificate's `issuer` must be equal to the `subject` of the previous certificate.
        # 6. **CCR-6**: The root certificate must be `validFrom` before the intermediate certificate
        # 7. **CCR-7**: The `capabilities` of intermediate certificate must be a subset of the root cert
        # 8. **CCR-8**: The intermediate certificate's `subject` must be the delegate certificate `delegate`
        # 9. **CCR-9**: The intermediate certificate must be `validFrom` before the delegate certificate
        # 10. **CCR-10**: The root certificate's signature must be valid and signed by the root certificate's `issuer`.
        # 11. **CCR-11**: The intermediate certificate's signature must be valid and signed by the intermediate certificate's `issuer`.
        # 12. **CCR-12**: The delegate certificate's signature must be valid and signed by the `delegate`.

        # CCR-3
        self.assertIsInstance(cert_chain[0], EIP712DelegateCertificate)
        for i in [1, len(cert_chain) - 1]:
            self.assertIsInstance(cert_chain[i], EIP712AuthorityCertificate)

        # CCR-1
        chainId = cert_chain[2].chainId
        verifyingContract = cert_chain[2].verifyingContract
        for cert in cert_chain:
            self.assertEqual(cert.chainId, chainId)
            self.assertEqual(cert.verifyingContract, verifyingContract)

        # CCR-2
        realm = cert_chain[2].realm
        for cert in cert_chain[1:]:
            self.assertEqual(cert.realm, realm)

        # CCR-4
        self.assertEqual(cert_chain[2].subject, cert_chain[2].issuer)

        # CCR-5
        self.assertEqual(cert_chain[1].issuer, cert_chain[2].subject)

        # CCR-6
        self.assertLessEqual(cert_chain[2].validFrom, cert_chain[1].validFrom)

        # CCR-7
        self.assertTrue(cert_chain[2].capabilities == cert_chain[2].capabilities | cert_chain[1].capabilities)

        # CCR-8
        self.assertEqual(cert_chain[1].subject, cert_chain[0].delegate)

        # CCR-9
        self.assertLessEqual(cert_chain[1].validFrom, cert_chain[0].validFrom)

        # CCR-10
        _issuer = cert_chain[2].recover(a2b_hex(cert_sigs[2]))
        self.assertEqual(_issuer, trustroot_eth_key.address(binary=True))

        # CCR-11
        _issuer = cert_chain[1].recover(a2b_hex(cert_sigs[1]))
        self.assertEqual(_issuer, trustroot_eth_key.address(binary=True))

        # CCR-12
        _issuer = cert_chain[0].recover(a2b_hex(cert_sigs[0]))
        self.assertEqual(_issuer, delegate_eth_key.address(binary=True))

        yield self._sm.close()

    @inlineCallbacks
    def test_eip712_verify_certificate_chain_highlevel(self):
        yield self._sm.open()

        # keys originally used to sign the certificates in the certificate chain
        trustroot_eth_key: EthereumKey = self._sm[0]
        delegate_eth_key: EthereumKey = self._sm[1]
        delegate_cs_key: CryptosignKey = self._sm[6]

        certificates = parse_certificate_chain(self._certs_expected1)

        self.assertEqual(certificates[2].issuer, trustroot_eth_key.address(binary=True))

        self.assertEqual(certificates[0].delegate, delegate_eth_key.address(binary=True))
        self.assertEqual(certificates[0].csPubKey, delegate_cs_key.public_key(binary=True))

        yield self._sm.close()
