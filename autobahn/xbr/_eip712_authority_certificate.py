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

from autobahn.wamp.message import _URI_PAT_REALM_NAME_ETH

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
        'chainId',
        'verifyingContract',
        'validFrom',
        'issuer',
        'subject',
        'realm',
        'capabilities',
        'meta',
    )

    def __init__(self, chainId: int, verifyingContract: bytes, validFrom: int, issuer: bytes, subject: bytes,
                 realm: bytes, capabilities: int, meta: str):
        super().__init__(chainId, verifyingContract, validFrom)
        self.issuer = issuer
        self.subject = subject
        self.realm = realm
        self.capabilities = capabilities
        self.meta = meta

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

    @staticmethod
    def parse(data) -> 'EIP712AuthorityCertificate':
        if type(data) != dict:
            raise ValueError('invalid type {} for EIP712AuthorityCertificate'.format(type(data)))
        for k in data:
            if k not in ['chainId', 'verifyingContract', 'validFrom', 'issuer', 'subject',
                         'realm', 'capabilities', 'meta']:
                raise ValueError('invalid attribute "{}" in EIP712AuthorityCertificate'.format(k))

        chainId = data.get('chainId', None)
        if chainId is None:
            raise ValueError('missing chainId in EIP712AuthorityCertificate')
        if type(chainId) != int:
            raise ValueError('invalid type {} for chainId in EIP712AuthorityCertificate'.format(type(chainId)))

        verifyingContract = data.get('verifyingContract', None)
        if verifyingContract is None:
            raise ValueError('missing verifyingContract in EIP712AuthorityCertificate')
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
        if type(issuer) != str:
            raise ValueError('invalid type {} for issuer in EIP712AuthorityCertificate'.format(type(issuer)))
        if not _URI_PAT_REALM_NAME_ETH.match(issuer):
            raise ValueError('invalid value "{}" for issuer in EIP712AuthorityCertificate'.format(issuer))
        issuer = a2b_hex(issuer[2:])

        subject = data.get('subject', None)
        if subject is None:
            raise ValueError('missing subject in EIP712AuthorityCertificate')
        if type(subject) != str:
            raise ValueError('invalid type {} for subject in EIP712AuthorityCertificate'.format(type(subject)))
        if not _URI_PAT_REALM_NAME_ETH.match(subject):
            raise ValueError('invalid value "{}" for subject in EIP712AuthorityCertificate'.format(subject))
        subject = a2b_hex(subject[2:])

        realm = data.get('realm', None)
        if realm is None:
            raise ValueError('missing realm in EIP712AuthorityCertificate')
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
