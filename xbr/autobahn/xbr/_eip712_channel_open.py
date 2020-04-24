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
from py_eth_sig_utils import signing

_EIP712_SIG_LEN = 32 + 32 + 1


def _create_eip712_channel_open(chainId: int, verifyingContract: bytes, ctype: int, openedAt: int,
                                marketId: bytes, channelId: bytes, actor: bytes, delegate: bytes,
                                marketmaker: bytes, recipient: bytes, amount: int) -> dict:
    """

    :param chainId:
    :param verifyingContract:
    :param ctype:
    :param openedAt:
    :param marketId:
    :param channelId:
    :param actor:
    :param delegate:
    :param marketmaker:
    :param recipient:
    :param amount:
    :return:
    """
    assert type(chainId) == int
    assert type(verifyingContract) == bytes and len(verifyingContract) == 20
    assert type(ctype) == int
    assert type(openedAt) == int
    assert type(marketId) == bytes and len(marketId) == 16
    assert type(channelId) == bytes and len(channelId) == 16
    assert type(actor) == bytes and len(actor) == 20
    assert type(delegate) == bytes and len(delegate) == 20
    assert type(marketmaker) == bytes and len(marketmaker) == 20
    assert type(recipient) == bytes and len(recipient) == 20
    assert type(amount) == int

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
            'EIP712ChannelOpen': [{
                'name': 'chainId',
                'type': 'uint256'
            }, {
                'name': 'verifyingContract',
                'type': 'address'
            }, {
                'name': 'ctype',
                'type': 'uint8'
            }, {
                'name': 'openedAt',
                'type': 'uint256'
            }, {
                'name': 'marketId',
                'type': 'bytes16'
            }, {
                'name': 'channelId',
                'type': 'bytes16'
            }, {
                'name': 'actor',
                'type': 'address'
            }, {
                'name': 'delegate',
                'type': 'address'
            }, {
                'name': 'marketmaker',
                'type': 'address'
            }, {
                'name': 'recipient',
                'type': 'address'
            }, {
                'name': 'amount',
                'type': 'uint256'
            }]
        },
        'primaryType': 'EIP712ChannelOpen',
        'domain': {
            'name': 'XBR',
            'version': '1',
        },
        'message': {
            'chainId': chainId,
            'verifyingContract': verifyingContract,
            'ctype': ctype,
            'openedAt': openedAt,
            'marketId': marketId,
            'channelId': channelId,
            'actor': actor,
            'delegate': delegate,
            'marketmaker': marketmaker,
            'recipient': recipient,
            'amount': amount
        }
    }

    return data


def sign_eip712_channel_open(eth_privkey: bytes, chainId: int, verifyingContract: bytes, ctype: int,
                             openedAt: int, marketId: bytes, channelId: bytes, actor: bytes, delegate: bytes,
                             marketmaker: bytes, recipient: bytes, amount: int) -> bytes:
    """

    :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
    :type eth_privkey: bytes

    :return: The signature according to EIP712 (32+32+1 raw bytes).
    :rtype: bytes
    """
    # create EIP712 typed data object
    data = _create_eip712_channel_open(chainId, verifyingContract, ctype, openedAt, marketId, channelId,
                                       actor, delegate, marketmaker, recipient, amount)

    # FIXME: this fails on PyPy (but ot on CPy!) with
    #  Unknown format b'%M\xff\xcd2w\xc0\xb1f\x0fmB\xef\xbbuN\xda\xba\xbc+', attempted to normalize to 0x254dffcd3277c0b1660f6d42efbb754edababc2b
    _args = signing.sign_typed_data(data, eth_privkey)

    signature = signing.v_r_s_to_signature(*_args)
    assert len(signature) == _EIP712_SIG_LEN

    return signature


def recover_eip712_channel_open(chainId: int, verifyingContract: bytes, ctype: int, openedAt: int,
                                marketId: bytes, channelId: bytes, actor: bytes, delegate: bytes,
                                marketmaker: bytes, recipient: bytes, amount: int, signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    # create EIP712 typed data object
    data = _create_eip712_channel_open(chainId, verifyingContract, ctype, openedAt, marketId, channelId,
                                       actor, delegate, marketmaker, recipient, amount)

    assert type(signature) == bytes and len(signature) == _EIP712_SIG_LEN
    signer_address = signing.recover_typed_data(data, *signing.signature_to_v_r_s(signature))

    return a2b_hex(signer_address[2:])
