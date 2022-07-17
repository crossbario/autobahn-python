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

from binascii import a2b_hex
from typing import Dict, Any

import json

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
        'chainId',
        'verifyingContract',
        'validFrom',
        'delegate',
        'csPubKey',
        'bootedAt',
        'meta',
    )

    def __init__(self, chainId: int, verifyingContract: bytes, validFrom: int, delegate: bytes, csPubKey: bytes,
                 bootedAt: int, meta: str):
        super().__init__(chainId, verifyingContract, validFrom)
        self.delegate = delegate
        self.csPubKey = csPubKey
        self.bootedAt = bootedAt
        self.meta = meta

    def sign(self, key: EthereumKey) -> bytes:
        eip712 = create_eip712_delegate_certificate(self.chainId,
                                                    self.verifyingContract,
                                                    self.validFrom,
                                                    self.delegate,
                                                    self.csPubKey,
                                                    self.bootedAt,
                                                    self.meta)
        # FIXME
        data = json.dumps(eip712).encode()
        return key.sign(data)

    def recover(self, signature: bytes) -> bytes:
        return recover_eip712_delegate_certificate(self.chainId,
                                                   self.verifyingContract,
                                                   self.validFrom,
                                                   self.delegate,
                                                   self.csPubKey,
                                                   self.bootedAt,
                                                   self.meta,
                                                   signature)

    def marshal(self) -> Dict[str, Any]:
        return create_eip712_delegate_certificate(self.chainId,
                                                  self.verifyingContract,
                                                  self.validFrom,
                                                  self.delegate,
                                                  self.csPubKey,
                                                  self.bootedAt,
                                                  self.meta)

    @staticmethod
    def parse(data) -> 'EIP712DelegateCertificate':
        if type(data) != dict:
            raise ValueError('invalid type {} for EIP712DelegateCertificate'.format(type(data)))
        for k in data:
            if k not in ['chainId', 'verifyingContract', 'delegate', 'validFrom', 'csPubKey', 'bootedAt', 'meta']:
                raise ValueError('invalid attribute "{}" in EIP712DelegateCertificate'.format(k))

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
