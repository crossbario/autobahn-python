# coding=utf8
# XBR Network - Copyright (c) Crossbar.io Technologies GmbH. All rights reserved.

from xbrnetwork._eip712_base import sign, recover, is_address, is_bytes16


def _create_eip712_api_publish(chainId: int, verifyingContract: bytes, member: bytes, published: int,
                               catalogId: bytes, apiId: bytes, schema: str, meta: str) -> dict:
    """

    :param chainId:
    :param verifyingContract:
    :param member:
    :param published:
    :param catalogId:
    :param apiId:
    :param schema:
    :param meta:
    :return:
    """
    assert type(chainId) == int
    assert is_address(verifyingContract)
    assert is_address(member)
    assert type(published) == int
    assert is_bytes16(catalogId)
    assert is_bytes16(apiId)
    assert type(schema) == str
    assert type(meta) == str

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
            'EIP712ApiPublish': [
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
                    'name': 'published',
                    'type': 'uint256'
                },
                {
                    'name': 'catalogId',
                    'type': 'bytes16'
                },
                {
                    'name': 'apiId',
                    'type': 'bytes16'
                },
                {
                    'name': 'schema',
                    'type': 'string'
                },
                {
                    'name': 'meta',
                    'type': 'string'
                },
            ]
        },
        'primaryType': 'EIP712ApiPublish',
        'domain': {
            'name': 'XBR',
            'version': '1',
        },
        'message': {
            'chainId': chainId,
            'verifyingContract': verifyingContract,
            'member': member,
            'published': published,
            'catalogId': catalogId,
            'apiId': apiId,
            'schema': schema,
            'meta': meta or '',
        }
    }

    return data


def sign_eip712_api_publish(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes,
                            published: int, catalogId: bytes, apiId: bytes, schema: str, meta: str) -> bytes:
    """

    :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
    :type eth_privkey: bytes

    :return: The signature according to EIP712 (32+32+1 raw bytes).
    :rtype: bytes
    """
    # create EIP712 typed data object
    data = _create_eip712_api_publish(chainId, verifyingContract, member, published, catalogId, apiId, schema,
                                      meta)
    return sign(eth_privkey, data)


def recover_eip712_api_publish(chainId: int, verifyingContract: bytes, member: bytes, published: int,
                               catalogId: bytes, apiId: bytes, schema: str, meta: str,
                               signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    # recreate EIP712 typed data object
    data = _create_eip712_api_publish(chainId, verifyingContract, member, published, catalogId, apiId, schema,
                                      meta)
    return recover(data, signature)
