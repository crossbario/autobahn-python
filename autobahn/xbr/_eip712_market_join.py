# coding=utf8
# XBR Network - Copyright (c) Crossbar.io Technologies GmbH. All rights reserved.

from binascii import a2b_hex
from py_eth_sig_utils import signing

_EIP712_SIG_LEN = 32 + 32 + 1


def _create_eip712_market_join(chainId: int, verifyingContract: bytes, member: bytes, joined: int,
                               marketId: bytes, actorType: int, meta: str) -> dict:
    """

    :param chainId:
    :param verifyingContract:
    :param member:
    :param joined:
    :param marketId:
    :param actorType:
    :param meta:
    :return:
    """
    assert type(chainId) == int
    assert type(verifyingContract) == bytes and len(verifyingContract) == 20
    assert type(member) == bytes and len(member) == 20
    assert type(joined) == int
    assert type(marketId) == bytes and len(marketId) == 16
    assert type(actorType) == int
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
            'EIP712MarketJoin': [
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
                    'name': 'joined',
                    'type': 'uint256'
                },
                {
                    'name': 'marketId',
                    'type': 'bytes16'
                },
                {
                    'name': 'actorType',
                    'type': 'uint8'
                },
                {
                    'name': 'meta',
                    'type': 'string',
                },
            ]
        },
        'primaryType': 'EIP712MarketJoin',
        'domain': {
            'name': 'XBR',
            'version': '1',
        },
        'message': {
            'chainId': chainId,
            'verifyingContract': verifyingContract,
            'member': member,
            'joined': joined,
            'marketId': marketId,
            'actorType': actorType,
            'meta': meta or '',
        }
    }

    return data


def sign_eip712_market_join(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes,
                            joined: int, marketId: bytes, actorType: int, meta: str) -> bytes:
    """

    :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
    :type eth_privkey: bytes

    :return: The signature according to EIP712 (32+32+1 raw bytes).
    :rtype: bytes
    """
    assert type(eth_privkey) == bytes and len(eth_privkey) == 32
    assert type(chainId) == int
    assert type(verifyingContract) == bytes and len(verifyingContract) == 20
    assert type(member) == bytes and len(member) == 20
    assert type(joined) == int
    assert type(marketId) == bytes and len(marketId) == 16
    assert type(actorType) == int
    assert meta is None or type(meta) == str

    # make a private key object from the raw private key bytes
    # pkey = eth_keys.keys.PrivateKey(eth_privkey)

    # get the canonical address of the account
    # eth_adr = web3.Web3.toChecksumAddress(pkey.public_key.to_canonical_address())
    # eth_adr = pkey.public_key.to_canonical_address()

    # create EIP712 typed data object
    data = _create_eip712_market_join(chainId, verifyingContract, member, joined, marketId, actorType, meta)

    # FIXME: this fails on PyPy (but ot on CPy!) with
    #  Unknown format b'%M\xff\xcd2w\xc0\xb1f\x0fmB\xef\xbbuN\xda\xba\xbc+', attempted to normalize to 0x254dffcd3277c0b1660f6d42efbb754edababc2b
    _args = signing.sign_typed_data(data, eth_privkey)

    signature = signing.v_r_s_to_signature(*_args)
    assert len(signature) == _EIP712_SIG_LEN

    return signature


def recover_eip712_market_join(chainId: int, verifyingContract: bytes, member: bytes, joined: int,
                               marketId: bytes, actorType: int, meta: str, signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    assert type(chainId) == int
    assert type(verifyingContract) == bytes and len(verifyingContract) == 20
    assert type(member) == bytes and len(member) == 20
    assert type(joined) == int
    assert type(marketId) == bytes and len(marketId) == 16
    assert type(actorType) == int
    assert meta is None or type(meta) == str
    assert type(signature) == bytes and len(signature) == _EIP712_SIG_LEN

    # recreate EIP712 typed data object
    data = _create_eip712_market_join(chainId, verifyingContract, member, joined, marketId, actorType, meta)

    # this returns the signer (checksummed) address as a string, eg "0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d"
    signer_address = signing.recover_typed_data(data, *signing.signature_to_v_r_s(signature))

    return a2b_hex(signer_address[2:])
