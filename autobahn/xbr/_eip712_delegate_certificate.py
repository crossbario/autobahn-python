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
import pprint
from typing import Dict, Any, Optional, List
from binascii import a2b_hex, b2a_hex

import web3
import cbor2

from py_eth_sig_utils.eip712 import encode_typed_data

from autobahn.wamp.message import _URI_PAT_REALM_NAME_ETH
from autobahn.xbr._secmod import EthereumKey

from ._eip712_base import sign, recover, is_chain_id, is_address, is_cs_pubkey, \
    is_block_number, is_signature, is_eth_privkey
from ._eip712_certificate import EIP712Certificate


def create_eip712_delegate_certificate(chainId: int,
                                       verifyingContract: bytes,
                                       validFrom: int,
                                       delegate: bytes,
                                       csPubKey: bytes,
                                       bootedAt: int,
                                       meta: str) -> dict:
    """
    Delegate certificate: dynamic/one-time, off-chain.

    :param chainId:
    :param verifyingContract:
    :param validFrom:
    :param delegate:
    :param csPubKey:
    :param bootedAt:
    :param meta:
    :return:
    """
    assert is_chain_id(chainId)
    assert is_address(verifyingContract)
    assert is_block_number(validFrom)
    assert is_address(delegate)
    assert is_cs_pubkey(csPubKey)
    assert type(bootedAt) == int
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
            'EIP712DelegateCertificate': [
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
                    'name': 'delegate',
                    'type': 'address'
                },
                {
                    'name': 'csPubKey',
                    'type': 'bytes32'
                },
                {
                    'name': 'bootedAt',
                    'type': 'uint64'
                },
                {
                    'name': 'meta',
                    'type': 'string'
                }
            ]
        },
        'primaryType': 'EIP712DelegateCertificate',
        'domain': {
            'name': 'WMP',
            'version': '1',
        },
        'message': {
            'chainId': chainId,
            'verifyingContract': verifyingContract,
            'validFrom': validFrom,
            'delegate': delegate,
            'csPubKey': csPubKey,
            'bootedAt': bootedAt,
            'meta': meta or '',
        }
    }

    return data


def sign_eip712_delegate_certificate(eth_privkey: bytes,
                                     chainId: int,
                                     verifyingContract: bytes,
                                     validFrom: int,
                                     delegate: bytes,
                                     csPubKey: bytes,
                                     bootedAt: int,
                                     meta: str) -> bytes:
    """
    Sign the given data using a EIP712 based signature with the provided private key.

    :param eth_privkey: Signing key.
    :param chainId:
    :param verifyingContract:
    :param validFrom:
    :param delegate:
    :param csPubKey:
    :param bootedAt:
    :param meta:
    :return: The signature according to EIP712 (32+32+1 raw bytes).
    """
    assert is_eth_privkey(eth_privkey)

    data = create_eip712_delegate_certificate(chainId, verifyingContract, validFrom, delegate,
                                              csPubKey, bootedAt, meta)
    return sign(eth_privkey, data)


def recover_eip712_delegate_certificate(chainId: int,
                                        verifyingContract: bytes,
                                        validFrom: int,
                                        delegate: bytes,
                                        csPubKey: bytes,
                                        bootedAt: int,
                                        meta: str,
                                        signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :param chainId:
    :param verifyingContract:
    :param validFrom:
    :param delegate:
    :param csPubKey:
    :param bootedAt:
    :param signature:
    :param meta:
    :return: The (computed) signer address the signature was signed with.
    """
    assert is_signature(signature)

    data = create_eip712_delegate_certificate(chainId, verifyingContract, validFrom, delegate,
                                              csPubKey, bootedAt, meta)
    return recover(data, signature)


class EIP712DelegateCertificate(EIP712Certificate):
    __slots__ = (
        # EIP712 attributes
        'chainId',
        'verifyingContract',
        'validFrom',
        'delegate',
        'csPubKey',
        'bootedAt',
        'meta',

        # additional attributes
        'signatures',
        'hash',
    )

    def __init__(self, chainId: int, verifyingContract: bytes, validFrom: int, delegate: bytes, csPubKey: bytes,
                 bootedAt: int, meta: str, signatures: Optional[List[bytes]] = None):
        super().__init__(chainId, verifyingContract, validFrom)
        self.delegate = delegate
        self.csPubKey = csPubKey
        self.bootedAt = bootedAt
        self.meta = meta
        self.signatures = signatures
        eip712 = create_eip712_delegate_certificate(chainId,
                                                    verifyingContract,
                                                    validFrom,
                                                    delegate,
                                                    csPubKey,
                                                    bootedAt,
                                                    meta)
        self.hash = encode_typed_data(eip712)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        if not EIP712DelegateCertificate.__eq__(self, other):
            return False
        if other.chainId != self.chainId:
            return False
        if other.verifyingContract != self.verifyingContract:
            return False
        if other.validFrom != self.validFrom:
            return False
        if other.delegate != self.delegate:
            return False
        if other.csPubKey != self.csPubKey:
            return False
        if other.bootedAt != self.bootedAt:
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
        eip712 = create_eip712_delegate_certificate(self.chainId,
                                                    self.verifyingContract,
                                                    self.validFrom,
                                                    self.delegate,
                                                    self.csPubKey,
                                                    self.bootedAt,
                                                    self.meta)
        return key.sign_typed_data(eip712, binary=binary)

    def recover(self, signature: bytes) -> bytes:
        return recover_eip712_delegate_certificate(self.chainId,
                                                   self.verifyingContract,
                                                   self.validFrom,
                                                   self.delegate,
                                                   self.csPubKey,
                                                   self.bootedAt,
                                                   self.meta,
                                                   signature)

    def marshal(self, binary: bool = False) -> Dict[str, Any]:
        obj = create_eip712_delegate_certificate(chainId=self.chainId,
                                                 verifyingContract=self.verifyingContract,
                                                 validFrom=self.validFrom,
                                                 delegate=self.delegate,
                                                 csPubKey=self.csPubKey,
                                                 bootedAt=self.bootedAt,
                                                 meta=self.meta)
        if not binary:
            obj['message']['verifyingContract'] = web3.Web3.toChecksumAddress(obj['message']['verifyingContract']) if obj['message']['verifyingContract'] else None
            obj['message']['delegate'] = web3.Web3.toChecksumAddress(obj['message']['delegate']) if obj['message']['delegate'] else None
            obj['message']['csPubKey'] = b2a_hex(obj['message']['csPubKey']).decode() if obj['message']['csPubKey'] else None
        return obj

    @staticmethod
    def parse(obj) -> 'EIP712DelegateCertificate':
        if type(obj) != dict:
            raise ValueError('invalid type {} for object in EIP712DelegateCertificate.parse'.format(type(obj)))

        primaryType = obj.get('primaryType', None)
        if primaryType != 'EIP712DelegateCertificate':
            raise ValueError('invalid primaryType "{}" - expected "EIP712DelegateCertificate"'.format(primaryType))

        # FIXME: check EIP712 types, domain

        data = obj.get('message', None)
        if type(data) != dict:
            raise ValueError('invalid type {} for EIP712DelegateCertificate'.format(type(data)))
        for k in data:
            if k not in ['type', 'chainId', 'verifyingContract', 'delegate', 'validFrom', 'csPubKey', 'bootedAt', 'meta']:
                raise ValueError('invalid attribute "{}" in EIP712DelegateCertificate'.format(k))

        _type = data.get('type', None)
        if _type and _type != 'EIP712DelegateCertificate':
            raise ValueError('unexpected type "{}" in EIP712DelegateCertificate'.format(_type))

        chainId = data.get('chainId', None)
        if chainId is None:
            raise ValueError('missing chainId in EIP712DelegateCertificate')
        if type(chainId) != int:
            raise ValueError('invalid type {} for chainId in EIP712DelegateCertificate'.format(type(chainId)))

        verifyingContract = data.get('verifyingContract', None)
        if verifyingContract is None:
            raise ValueError('missing verifyingContract in EIP712DelegateCertificate')
        if type(verifyingContract) != str:
            raise ValueError(
                'invalid type {} for verifyingContract in EIP712DelegateCertificate'.format(type(verifyingContract)))
        if not _URI_PAT_REALM_NAME_ETH.match(verifyingContract):
            raise ValueError(
                'invalid value "{}" for verifyingContract in EIP712DelegateCertificate'.format(verifyingContract))
        verifyingContract = a2b_hex(verifyingContract[2:])

        validFrom = data.get('validFrom', None)
        if validFrom is None:
            raise ValueError('missing validFrom in EIP712DelegateCertificate')
        if type(validFrom) != int:
            raise ValueError('invalid type {} for validFrom in EIP712DelegateCertificate'.format(type(validFrom)))

        delegate = data.get('delegate', None)
        if delegate is None:
            raise ValueError('missing delegate in EIP712DelegateCertificate')
        if type(delegate) != str:
            raise ValueError('invalid type {} for delegate in EIP712DelegateCertificate'.format(type(delegate)))
        if not _URI_PAT_REALM_NAME_ETH.match(delegate):
            raise ValueError('invalid value "{}" for verifyingContract in EIP712DelegateCertificate'.format(delegate))
        delegate = a2b_hex(delegate[2:])

        csPubKey = data.get('csPubKey', None)
        if csPubKey is None:
            raise ValueError('missing csPubKey in EIP712DelegateCertificate')
        if type(csPubKey) != str:
            raise ValueError('invalid type {} for csPubKey in EIP712DelegateCertificate'.format(type(csPubKey)))
        if len(csPubKey) != 64:
            raise ValueError('invalid value "{}" for csPubKey in EIP712DelegateCertificate'.format(csPubKey))
        csPubKey = a2b_hex(csPubKey)

        bootedAt = data.get('bootedAt', None)
        if bootedAt is None:
            raise ValueError('missing bootedAt in EIP712DelegateCertificate')
        if type(bootedAt) != int:
            raise ValueError('invalid type {} for bootedAt in EIP712DelegateCertificate'.format(type(bootedAt)))

        meta = data.get('meta', None)
        if meta is None:
            raise ValueError('missing meta in EIP712DelegateCertificate')
        if type(meta) != str:
            raise ValueError('invalid type {} for meta in EIP712DelegateCertificate'.format(type(meta)))

        obj = EIP712DelegateCertificate(chainId=chainId, verifyingContract=verifyingContract, validFrom=validFrom,
                                        delegate=delegate, csPubKey=csPubKey, bootedAt=bootedAt, meta=meta)
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
    def load(filename) -> 'EIP712DelegateCertificate':
        if not os.path.isfile(filename):
            raise RuntimeError('cannot create EIP712DelegateCertificate from filename "{}": not a file'.format(filename))
        with open(filename, 'rb') as f:
            cert_hash, cert_eip712, cert_signatures = cbor2.loads(f.read())
            cert = EIP712DelegateCertificate.parse(cert_eip712, binary=True)
            assert cert_hash == cert.hash
            cert.signatures = cert_signatures
            return cert
