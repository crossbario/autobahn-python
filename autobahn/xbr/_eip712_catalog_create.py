# coding=utf8
# XBR Network - Copyright (c) Crossbar.io Technologies GmbH. All rights reserved.
from typing import Optional
from xbrnetwork._eip712_base import sign, recover


def _create_eip712_catalog_create(chainId: int, verifyingContract: bytes, member: bytes, created: int,
                                  catalogId: bytes, terms: str, meta: Optional[str]) -> dict:
    """

    :param chainId:
    :param verifyingContract:
    :param member:
    :param created:
    :param catalogId:
    :param terms:
    :param meta:
    :return:
    """
    assert len(verifyingContract) == 20, 'Invalid contract'
    assert len(member) == 20, 'Invalid member oid'
    assert len(catalogId) == 16, 'Invalid catalog id'

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
            'EIP712CatalogCreate': [
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
                    'name': 'catalogId',
                    'type': 'bytes16'
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
        'primaryType': 'EIP712CatalogCreate',
        'domain': {
            'name': 'XBR',
            'version': '1',
        },
        'message': {
            'chainId': chainId,
            'verifyingContract': verifyingContract,
            'member': member,
            'created': created,
            'catalogId': catalogId,
            'terms': terms,
            'meta': meta or '',
        }
    }

    return data


def sign_eip712_catalog_create(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes,
                               created: int, catalogId: bytes, terms: str, meta: str) -> bytes:
    """

    :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
    :type eth_privkey: bytes

    :return: The signature according to EIP712 (32+32+1 raw bytes).
    :rtype: bytes
    """
    # create EIP712 typed data object
    data = _create_eip712_catalog_create(chainId, verifyingContract, member, created, catalogId, terms, meta)
    return sign(eth_privkey, data)


def recover_eip712_catalog_create(chainId: int, verifyingContract: bytes, member: bytes, created: int,
                                  catalogId: bytes, terms: str, meta: str, signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    # recreate EIP712 typed data object
    data = _create_eip712_catalog_create(chainId, verifyingContract, member, created, catalogId, terms, meta)
    return recover(data, signature)
