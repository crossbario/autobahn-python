# coding=utf8
# XBR Network - Copyright (c) Crossbar.io Technologies GmbH. All rights reserved.
from xbrnetwork._eip712_base import sign, recover, is_address, is_bytes16


def _create_eip712_consent(chainId: int, verifyingContract: bytes, member: bytes, updated: int,
                           marketId: bytes, delegate: bytes, delegateType: int, apiCatalog: bytes,
                           consent: bool, servicePrefix: str) -> dict:
    """

    :param chainId:
    :param verifyingContract:
    :param member:
    :param updated:
    :param marketId:
    :param delegate:
    :param delegateType:
    :param apiCatalog:
    :param consent:
    :param servicePrefix:
    :return:
    """
    assert type(chainId) == int
    assert is_address(verifyingContract)
    assert is_address(member)
    assert type(updated) == int
    assert is_bytes16(marketId)
    assert is_address(delegate)
    assert type(delegateType) == int
    assert is_bytes16(apiCatalog)
    assert type(consent) == bool
    assert servicePrefix is None or type(servicePrefix) == str

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
            'EIP712Consent': [
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
                    'name': 'updated',
                    'type': 'uint256'
                },
                {
                    'name': 'marketId',
                    'type': 'bytes16'
                },
                {
                    'name': 'delegate',
                    'type': 'address'
                },
                {
                    'name': 'delegateType',
                    'type': 'uint8'
                },
                {
                    'name': 'apiCatalog',
                    'type': 'bytes16'
                },
                {
                    'name': 'consent',
                    'type': 'bool'
                },
                {
                    'name': 'servicePrefix',
                    'type': 'string'
                },
            ]
        },
        'primaryType': 'EIP712Consent',
        'domain': {
            'name': 'XBR',
            'version': '1',
        },
        'message': {
            'chainId': chainId,
            'verifyingContract': verifyingContract,
            'member': member,
            'updated': updated,
            'marketId': marketId,
            'delegate': delegate,
            'delegateType': delegateType,
            'apiCatalog': apiCatalog,
            'consent': consent,
            'servicePrefix': servicePrefix or ''
        }
    }

    return data


def sign_eip712_consent(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes,
                        updated: int, marketId: bytes, delegate: bytes, delegateType: int, apiCatalog: bytes,
                        consent: bool, servicePrefix: str) -> bytes:
    """

    :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
    :type eth_privkey: bytes

    :return: The signature according to EIP712 (32+32+1 raw bytes).
    :rtype: bytes
    """
    # create EIP712 typed data object
    data = _create_eip712_consent(chainId, verifyingContract, member, updated, marketId, delegate,
                                  delegateType, apiCatalog, consent, servicePrefix)
    return sign(eth_privkey, data)


def recover_eip712_consent(chainId: int, verifyingContract: bytes, member: bytes, updated: int,
                           marketId: bytes, delegate: bytes, delegateType: int, apiCatalog: bytes,
                           consent: bool, servicePrefix: str, signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    # create EIP712 typed data object
    data = _create_eip712_consent(chainId, verifyingContract, member, updated, marketId, delegate,
                                  delegateType, apiCatalog, consent, servicePrefix)
    return recover(data, signature)
