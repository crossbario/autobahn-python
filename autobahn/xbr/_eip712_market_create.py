# coding=utf8
# XBR Network - Copyright (c) Crossbar.io Technologies GmbH. All rights reserved.

from xbrnetwork._eip712_base import sign, recover


def _create_eip712_market_create(chainId: int, verifyingContract: bytes, member: bytes, created: int,
                                 marketId: bytes, coin: bytes, terms: str, meta: str, maker: bytes,
                                 providerSecurity: int, consumerSecurity: int, marketFee: int) -> dict:
    """

    :param chainId:
    :param verifyingContract:
    :param member:
    :param created:
    :param marketId:
    :param coin:
    :param terms:
    :param meta:
    :param maker:
    :param providerSecurity:
    :param consumerSecurity:
    :param marketFee:
    :return:
    """
    assert type(chainId) == int
    assert type(verifyingContract) == bytes and len(verifyingContract) == 20
    assert type(member) == bytes and len(member) == 20
    assert type(created) == int
    assert type(marketId) == bytes and len(marketId) == 16
    assert type(coin) == bytes and len(coin) == 20
    assert type(terms) == str
    assert type(meta) == str
    assert type(maker) == bytes and len(maker) == 20
    assert type(providerSecurity) == int
    assert type(consumerSecurity) == int
    assert type(marketFee) == int

    # FIXME: add "coin" in below once we have done that in XBRTypes

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
            'EIP712MarketCreate': [{
                'name': 'chainId',
                'type': 'uint256'
            }, {
                'name': 'verifyingContract',
                'type': 'address'
            }, {
                'name': 'member',
                'type': 'address'
            }, {
                'name': 'created',
                'type': 'uint256'
            }, {
                'name': 'marketId',
                'type': 'bytes16'
            }, {
                'name': 'coin',
                'type': 'address'
            }, {
                'name': 'terms',
                'type': 'string'
            }, {
                'name': 'meta',
                'type': 'string'
            }, {
                'name': 'maker',
                'type': 'address'
            }, {
                'name': 'marketFee',
                'type': 'uint256',
            }]
        },
        'primaryType': 'EIP712MarketCreate',
        'domain': {
            'name': 'XBR',
            'version': '1',
        },
        'message': {
            'chainId': chainId,
            'verifyingContract': verifyingContract,
            'member': member,
            'created': created,
            'marketId': marketId,
            'coin': coin,
            'terms': terms or '',
            'meta': meta or '',
            'maker': maker,
            'marketFee': marketFee,
        }
    }

    return data


def sign_eip712_market_create(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes,
                              created: int, marketId: bytes, coin: bytes, terms: str, meta: str, maker: bytes,
                              providerSecurity: int, consumerSecurity: int, marketFee: int) -> bytes:
    """

    :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
    :type eth_privkey: bytes

    :return: The signature according to EIP712 (32+32+1 raw bytes).
    :rtype: bytes
    """
    # create EIP712 typed data object
    data = _create_eip712_market_create(chainId, verifyingContract, member, created, marketId, coin, terms,
                                        meta, maker, providerSecurity, consumerSecurity, marketFee)
    return sign(eth_privkey, data)


def recover_eip712_market_create(chainId: int, verifyingContract: bytes, member: bytes, created: int,
                                 marketId: bytes, coin: bytes, terms: str, meta: str, maker: bytes,
                                 providerSecurity: int, consumerSecurity: int, marketFee: int,
                                 signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    # create EIP712 typed data object
    data = _create_eip712_market_create(chainId, verifyingContract, member, created, marketId, coin, terms,
                                        meta, maker, providerSecurity, consumerSecurity, marketFee)

    return recover(data, signature)