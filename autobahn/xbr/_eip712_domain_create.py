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

from typing import Optional
from ._eip712_base import sign, recover, is_chain_id, is_address, is_bytes16, is_cs_pubkey, \
    is_block_number, is_signature, is_eth_privkey


def _create_eip712_domain_create(chainId: int, verifyingContract: bytes, member: bytes, created: int,
                                 domainId: bytes, domainKey: bytes, license: str, terms: str,
                                 meta: Optional[str]) -> dict:
    """

    :param chainId:
    :param verifyingContract:
    :param member:
    :param created:
    :param domainId:
    :param domainKey:
    :param license:
    :param terms:
    :param meta:
    :return:
    """
    assert is_chain_id(chainId)
    assert is_address(verifyingContract)
    assert is_address(member)
    assert is_block_number(created)
    assert is_bytes16(domainId)
    assert is_cs_pubkey(domainKey)

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
            'EIP712DomainCreate': [
                {
                    'name': 'chainId',
                    'type': 'uint256'
                },
                {
                    'name': 'verifyingContract',
                    'type': 'address'
                },
                {
                    'name': 'member',
                    'type': 'address'
                },
                {
                    'name': 'created',
                    'type': 'uint256'
                },
                {
                    'name': 'domainId',
                    'type': 'bytes16'
                },
                {
                    'name': 'domainKey',
                    'type': 'bytes32'
                },
                {
                    'name': 'license',
                    'type': 'string'
                },
                {
                    'name': 'terms',
                    'type': 'string'
                },
                {
                    'name': 'meta',
                    'type': 'string'
                },
            ]
        },
        'primaryType': 'EIP712DomainCreate',
        'domain': {
            'name': 'XBR',
            'version': '1',
        },
        'message': {
            'chainId': chainId,
            'verifyingContract': verifyingContract,
            'member': member,
            'created': created,
            'domainId': domainId,
            'domainKey': domainKey,
            'license': license,
            'terms': terms,
            'meta': meta or '',
        }
    }

    return data


def sign_eip712_domain_create(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes, created: int,
                              domainId: bytes, domainKey: bytes, license: str, terms: str,
                              meta: str) -> bytes:
    """

    :param eth_privkey: Ethereum address of member (a raw 20 bytes Ethereum address).
    :type eth_privkey: bytes

    :return: The signature according to EIP712 (32+32+1 raw bytes).
    :rtype: bytes
    """
    assert is_eth_privkey(eth_privkey)
    assert is_chain_id(chainId)
    assert is_address(verifyingContract)
    assert is_address(member)
    assert is_block_number(created)
    assert is_bytes16(domainId)
    assert is_cs_pubkey(domainKey)

    data = _create_eip712_domain_create(chainId, verifyingContract, member, created, domainId, domainKey, license,
                                        terms, meta)
    return sign(eth_privkey, data)


def recover_eip712_domain_create(chainId: int, verifyingContract: bytes, member: bytes, created: int, domainId: bytes,
                                 domainKey: bytes, license: str, terms: str, meta: str, signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    assert is_chain_id(chainId)
    assert is_address(verifyingContract)
    assert is_address(member)
    assert is_block_number(created)
    assert is_bytes16(domainId)
    assert is_cs_pubkey(domainKey)
    assert is_signature(signature)

    data = _create_eip712_domain_create(chainId, verifyingContract, member, created, domainId, domainKey, license,
                                        terms, meta)
    return recover(data, signature)
