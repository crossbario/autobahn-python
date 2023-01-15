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
import os.path
import pprint
from binascii import a2b_hex
from typing import Dict, Any, Optional, List

import web3
import cbor2

from py_eth_sig_utils.eip712 import encode_typed_data

from autobahn.wamp.message import _URI_PAT_REALM_NAME_ETH
from autobahn.xbr._secmod import EthereumKey

from ._eip712_base import sign, recover, is_chain_id, is_address, is_block_number, is_signature, is_eth_privkey
from ._eip712_certificate import EIP712Certificate


def create_eip712_authority_certificate(chainId: int,
                                        verifyingContract: bytes,
                                        validFrom: int,
                                        issuer: bytes,
                                        subject: bytes,
                                        realm: bytes,
                                        capabilities: int,
                                        meta: str) -> dict:
    """
    Authority certificate: long-lived, on-chain L2.

    :param chainId:
    :param verifyingContract:
    :param validFrom:
    :param issuer:
    :param subject:
    :param realm:
    :param capabilities:
    :param meta:
    :return:
    """
    assert is_chain_id(chainId)
    assert is_address(verifyingContract)
    assert is_block_number(validFrom)
    assert is_address(issuer)
    assert is_address(subject)
    assert is_address(realm)
    assert type(capabilities) == int and 0 <= capabilities <= 2 ** 53
    assert meta is None or type(meta) == str

    data = {
        'types': {
            'EIP712Domain': [
                {
                    'name': 'name',
                    'type': 'string'
                },
                {
                    'name': 'version',
                    'type': 'string'
                },
            ],
            'EIP712AuthorityCertificate': [
                {
                    'name': 'chainId',
                    'type': 'uint256'
                },
                {
                    'name': 'verifyingContract',
                    'type': 'address'
                },
                {
                    'name': 'validFrom',
                    'type': 'uint256'
                },
                {
                    'name': 'issuer',
                    'type': 'address'
                },
                {
                    'name': 'subject',
                    'type': 'address'
                },
                {
                    'name': 'realm',
                    'type': 'address'
                },
                {
                    'name': 'capabilities',
                    'type': 'uint64'
                },
                {
                    'name': 'meta',
                    'type': 'string'
                }
            ]
        },
        'primaryType': 'EIP712AuthorityCertificate',
        'domain': {
            'name': 'WMP',
            'version': '1',
        },
        'message': {
            'chainId': chainId,
            'verifyingContract': verifyingContract,
            'validFrom': validFrom,
            'issuer': issuer,
            'subject': subject,
            'realm': realm,
            'capabilities': capabilities,
            'meta': meta or '',
        }
    }

    return data


def sign_eip712_authority_certificate(eth_privkey: bytes,
                                      chainId: int,
                                      verifyingContract: bytes,
                                      validFrom: int,
                                      issuer: bytes,
                                      subject: bytes,
                                      realm: bytes,
                                      capabilities: int,
                                      meta: str) -> bytes:
    """
    Sign the given data using a EIP712 based signature with the provided private key.

    :param eth_privkey:
    :param chainId:
    :param verifyingContract:
    :param validFrom:
    :param issuer:
    :param subject:
    :param realm:
    :param capabilities:
    :param meta:
    :return:
    """
    assert is_eth_privkey(eth_privkey)

    data = create_eip712_authority_certificate(chainId, verifyingContract, validFrom, issuer,
                                               subject, realm, capabilities, meta)
    return sign(eth_privkey, data)


def recover_eip712_authority_certificate(chainId: int,
                                         verifyingContract: bytes,
                                         validFrom: int,
                                         issuer: bytes,
                                         subject: bytes,
                                         realm: bytes,
                                         capabilities: int,
                                         meta: str,
                                         signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :param chainId:
    :param verifyingContract:
    :param validFrom:
    :param issuer:
    :param subject:
    :param realm:
    :param capabilities:
    :param meta:
    :param signature:
    :return: The (computed) signer address the signature was signed with.
    """
    assert is_signature(signature)

    data = create_eip712_authority_certificate(chainId, verifyingContract, validFrom, issuer,
                                               subject, realm, capabilities, meta)
    return recover(data, signature)


class EIP712AuthorityCertificate(EIP712Certificate):
    CAPABILITY_ROOT_CA = 1
    CAPABILITY_INTERMEDIATE_CA = 2
    CAPABILITY_PUBLIC_RELAY = 4
    CAPABILITY_PRIVATE_RELAY = 8
    CAPABILITY_PROVIDER = 16
    CAPABILITY_CONSUMER = 32

    __slots__ = (
        # EIP712 attributes
        'chainId',
        'verifyingContract',
        'validFrom',
        'issuer',
        'subject',
        'realm',
        'capabilities',
        'meta',

        # additional attributes
        'signatures',
        'hash',
    )

    def __init__(self, chainId: int, verifyingContract: bytes, validFrom: int, issuer: bytes, subject: bytes,
                 realm: bytes, capabilities: int, meta: str,
                 signatures: Optional[List[bytes]] = None):
        super().__init__(chainId, verifyingContract, validFrom)
        self.issuer = issuer
        self.subject = subject
        self.realm = realm
        self.capabilities = capabilities
        self.meta = meta
        self.signatures = signatures
        eip712 = create_eip712_authority_certificate(chainId,
                                                     verifyingContract,
                                                     validFrom,
                                                     issuer,
                                                     subject,
                                                     realm,
                                                     capabilities,
                                                     meta)
        self.hash = encode_typed_data(eip712)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        if not EIP712AuthorityCertificate.__eq__(self, other):
            return False
        if other.chainId != self.chainId:
            return False
        if other.verifyingContract != self.verifyingContract:
            return False
        if other.validFrom != self.validFrom:
            return False
        if other.issuer != self.issuer:
            return False
        if other.subject != self.subject:
            return False
        if other.realm != self.realm:
            return False
        if other.capabilities != self.capabilities:
            return False
        if other.meta != self.meta:
            return False
        if other.signatures != self.signatures:
            return False
        if other.hash != self.hash:
            return False
        return True

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return pprint.pformat(self.marshal())

    def sign(self, key: EthereumKey, binary: bool = False) -> bytes:
        eip712 = create_eip712_authority_certificate(self.chainId,
                                                     self.verifyingContract,
                                                     self.validFrom,
                                                     self.issuer,
                                                     self.subject,
                                                     self.realm,
                                                     self.capabilities,
                                                     self.meta)
        return key.sign_typed_data(eip712, binary=binary)

    def recover(self, signature: bytes) -> bytes:
        return recover_eip712_authority_certificate(self.chainId,
                                                    self.verifyingContract,
                                                    self.validFrom,
                                                    self.issuer,
                                                    self.subject,
                                                    self.realm,
                                                    self.capabilities,
                                                    self.meta,
                                                    signature)

    def marshal(self, binary: bool = False) -> Dict[str, Any]:
        obj = create_eip712_authority_certificate(chainId=self.chainId,
                                                  verifyingContract=self.verifyingContract,
                                                  validFrom=self.validFrom,
                                                  issuer=self.issuer,
                                                  subject=self.subject,
                                                  realm=self.realm,
                                                  capabilities=self.capabilities,
                                                  meta=self.meta)
        if not binary:
            obj['message']['verifyingContract'] = web3.Web3.toChecksumAddress(obj['message']['verifyingContract']) if obj['message']['verifyingContract'] else None
            obj['message']['issuer'] = web3.Web3.toChecksumAddress(obj['message']['issuer']) if obj['message']['issuer'] else None
            obj['message']['subject'] = web3.Web3.toChecksumAddress(obj['message']['subject']) if obj['message']['subject'] else None
            obj['message']['realm'] = web3.Web3.toChecksumAddress(obj['message']['realm']) if obj['message']['realm'] else None
        return obj

    @staticmethod
    def parse(obj, binary: bool = False) -> 'EIP712AuthorityCertificate':
        if type(obj) != dict:
            raise ValueError('invalid type {} for object in EIP712AuthorityCertificate.parse'.format(type(obj)))

        primaryType = obj.get('primaryType', None)
        if primaryType != 'EIP712AuthorityCertificate':
            raise ValueError('invalid primaryType "{}" - expected "EIP712AuthorityCertificate"'.format(primaryType))

        # FIXME: check EIP712 types, domain

        data = obj.get('message', None)
        if type(data) != dict:
            raise ValueError('invalid type {} for EIP712AuthorityCertificate'.format(type(data)))
        for k in data:
            if k not in ['type', 'chainId', 'verifyingContract', 'validFrom', 'issuer', 'subject',
                         'realm', 'capabilities', 'meta']:
                raise ValueError('invalid attribute "{}" in EIP712AuthorityCertificate'.format(k))

        _type = data.get('type', None)
        if _type and _type != 'EIP712AuthorityCertificate':
            raise ValueError('unexpected type "{}" in EIP712AuthorityCertificate'.format(_type))

        chainId = data.get('chainId', None)
        if chainId is None:
            raise ValueError('missing chainId in EIP712AuthorityCertificate')
        if type(chainId) != int:
            raise ValueError('invalid type {} for chainId in EIP712AuthorityCertificate'.format(type(chainId)))

        verifyingContract = data.get('verifyingContract', None)
        if verifyingContract is None:
            raise ValueError('missing verifyingContract in EIP712AuthorityCertificate')
        if binary:
            if type(verifyingContract) != bytes:
                raise ValueError(
                    'invalid type {} for verifyingContract in EIP712AuthorityCertificate'.format(type(verifyingContract)))
            if len(verifyingContract) != 20:
                raise ValueError('invalid value length {} of verifyingContract'.format(len(verifyingContract)))
        else:
            if type(verifyingContract) != str:
                raise ValueError(
                    'invalid type {} for verifyingContract in EIP712AuthorityCertificate'.format(type(verifyingContract)))
            if not _URI_PAT_REALM_NAME_ETH.match(verifyingContract):
                raise ValueError(
                    'invalid value "{}" for verifyingContract in EIP712AuthorityCertificate'.format(verifyingContract))
            verifyingContract = a2b_hex(verifyingContract[2:])

        validFrom = data.get('validFrom', None)
        if validFrom is None:
            raise ValueError('missing validFrom in EIP712AuthorityCertificate')
        if type(validFrom) != int:
            raise ValueError('invalid type {} for validFrom in EIP712AuthorityCertificate'.format(type(validFrom)))

        issuer = data.get('issuer', None)
        if issuer is None:
            raise ValueError('missing issuer in EIP712AuthorityCertificate')
        if binary:
            if type(issuer) != bytes:
                raise ValueError(
                    'invalid type {} for issuer in EIP712AuthorityCertificate'.format(type(issuer)))
            if len(issuer) != 20:
                raise ValueError('invalid value length {} of issuer'.format(len(issuer)))
        else:
            if type(issuer) != str:
                raise ValueError('invalid type {} for issuer in EIP712AuthorityCertificate'.format(type(issuer)))
            if not _URI_PAT_REALM_NAME_ETH.match(issuer):
                raise ValueError('invalid value "{}" for issuer in EIP712AuthorityCertificate'.format(issuer))
            issuer = a2b_hex(issuer[2:])

        subject = data.get('subject', None)
        if subject is None:
            raise ValueError('missing subject in EIP712AuthorityCertificate')
        if binary:
            if type(subject) != bytes:
                raise ValueError(
                    'invalid type {} for subject in EIP712AuthorityCertificate'.format(type(subject)))
            if len(subject) != 20:
                raise ValueError('invalid value length {} of verifyingContract'.format(len(subject)))
        else:
            if type(subject) != str:
                raise ValueError('invalid type {} for subject in EIP712AuthorityCertificate'.format(type(subject)))
            if not _URI_PAT_REALM_NAME_ETH.match(subject):
                raise ValueError('invalid value "{}" for subject in EIP712AuthorityCertificate'.format(subject))
            subject = a2b_hex(subject[2:])

        realm = data.get('realm', None)
        if realm is None:
            raise ValueError('missing realm in EIP712AuthorityCertificate')
        if binary:
            if type(realm) != bytes:
                raise ValueError(
                    'invalid type {} for realm in EIP712AuthorityCertificate'.format(type(realm)))
            if len(realm) != 20:
                raise ValueError('invalid value length {} of realm'.format(len(realm)))
        else:
            if type(realm) != str:
                raise ValueError('invalid type {} for realm in EIP712AuthorityCertificate'.format(type(realm)))
            if not _URI_PAT_REALM_NAME_ETH.match(realm):
                raise ValueError('invalid value "{}" for realm in EIP712AuthorityCertificate'.format(realm))
            realm = a2b_hex(realm[2:])

        capabilities = data.get('capabilities', None)
        if capabilities is None:
            raise ValueError('missing capabilities in EIP712AuthorityCertificate')
        if type(capabilities) != int:
            raise ValueError('invalid type {} for capabilities in EIP712AuthorityCertificate'.format(type(capabilities)))

        meta = data.get('meta', None)
        if meta is None:
            raise ValueError('missing meta in EIP712AuthorityCertificate')
        if type(meta) != str:
            raise ValueError('invalid type {} for meta in EIP712AuthorityCertificate'.format(type(meta)))

        obj = EIP712AuthorityCertificate(chainId=chainId, verifyingContract=verifyingContract, validFrom=validFrom,
                                         issuer=issuer, subject=subject, realm=realm, capabilities=capabilities, meta=meta)
        return obj

    def save(self, filename: str) -> int:
        """
        Save certificate to file. File format (serialized as CBOR):

            [cert_hash: bytes, cert_eip712: Dict[str, Any], cert_signatures: List[bytes]]

        :param filename:
        :return:
        """
        cert_obj = [self.hash, self.marshal(binary=True), self.signatures or []]
        with open(filename, 'wb') as f:
            data = cbor2.dumps(cert_obj)
            f.write(data)
        return len(data)

    @staticmethod
    def load(filename) -> 'EIP712AuthorityCertificate':
        """
        Load certificate from file.

        :param filename:
        :return:
        """
        if not os.path.isfile(filename):
            raise RuntimeError('cannot create EIP712AuthorityCertificate from filename "{}": not a file'.format(filename))
        with open(filename, 'rb') as f:
            cert_hash, cert_eip712, cert_signatures = cbor2.loads(f.read())
            cert = EIP712AuthorityCertificate.parse(cert_eip712, binary=True)
            assert cert_hash == cert.hash
            cert.signatures = cert_signatures
            return cert
