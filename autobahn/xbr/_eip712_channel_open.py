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

from ._eip712_base import sign, recover, is_address, is_signature, is_eth_privkey, is_bytes16, \
    is_block_number, is_chain_id


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
    assert is_chain_id(chainId)
    assert is_address(verifyingContract)
    assert type(ctype) == int
    assert is_block_number(openedAt)
    assert is_bytes16(marketId)
    assert is_bytes16(channelId)
    assert is_address(actor)
    assert is_address(delegate)
    assert is_address(marketmaker)
    assert is_address(recipient)
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
    assert is_eth_privkey(eth_privkey)

    data = _create_eip712_channel_open(chainId, verifyingContract, ctype, openedAt, marketId, channelId,
                                       actor, delegate, marketmaker, recipient, amount)
    return sign(eth_privkey, data)


def recover_eip712_channel_open(chainId: int, verifyingContract: bytes, ctype: int, openedAt: int,
                                marketId: bytes, channelId: bytes, actor: bytes, delegate: bytes,
                                marketmaker: bytes, recipient: bytes, amount: int, signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    assert is_signature(signature)

    data = _create_eip712_channel_open(chainId, verifyingContract, ctype, openedAt, marketId, channelId,
                                       actor, delegate, marketmaker, recipient, amount)
    return recover(data, signature)
