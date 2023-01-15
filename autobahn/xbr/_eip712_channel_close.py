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


def _create_eip712_channel_close(chainId: int, verifyingContract: bytes, closeAt: int, marketId: bytes, channelId: bytes,
                                 channelSeq: int, balance: int, isFinal: bool) -> dict:
    """

    :param chainId:
    :param verifyingContract:
    :param marketId:
    :param channelId:
    :param channelSeq:
    :param balance:
    :param isFinal:
    :return:
    """
    assert is_chain_id(chainId)
    assert is_address(verifyingContract)
    assert is_block_number(closeAt)
    assert is_bytes16(marketId)
    assert is_bytes16(channelId)
    assert type(channelSeq) == int
    assert type(balance) == int
    assert type(isFinal) == bool

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
            'EIP712ChannelClose': [{
                'name': 'chainId',
                'type': 'uint256'
            }, {
                'name': 'verifyingContract',
                'type': 'address'
            }, {
                'name': 'closeAt',
                'type': 'uint256'
            }, {
                'name': 'marketId',
                'type': 'bytes16'
            }, {
                'name': 'channelId',
                'type': 'bytes16'
            }, {
                'name': 'channelSeq',
                'type': 'uint32'
            }, {
                'name': 'balance',
                'type': 'uint256'
            }, {
                'name': 'isFinal',
                'type': 'bool'
            }]
        },
        'primaryType': 'EIP712ChannelClose',
        'domain': {
            'name': 'XBR',
            'version': '1',
        },
        'message': {
            'chainId': chainId,
            'verifyingContract': verifyingContract,
            'closeAt': closeAt,
            'marketId': marketId,
            'channelId': channelId,
            'channelSeq': channelSeq,
            'balance': balance,
            'isFinal': isFinal
        }
    }

    return data


def sign_eip712_channel_close(eth_privkey: bytes, chainId: int, verifyingContract: bytes, closeAt: int, marketId: bytes,
                              channelId: bytes, channelSeq: int, balance: int, isFinal: bool) -> bytes:
    """

    :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
    :type eth_privkey: bytes

    :return: The signature according to EIP712 (32+32+1 raw bytes).
    :rtype: bytes
    """
    assert is_eth_privkey(eth_privkey)

    data = _create_eip712_channel_close(chainId, verifyingContract, closeAt, marketId, channelId, channelSeq, balance,
                                        isFinal)
    return sign(eth_privkey, data)


def recover_eip712_channel_close(chainId: int, verifyingContract: bytes, closeAt: int, marketId: bytes, channelId: bytes,
                                 channelSeq: int, balance: int, isFinal: bool, signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    assert is_signature(signature)

    data = _create_eip712_channel_close(chainId, verifyingContract, closeAt, marketId, channelId, channelSeq, balance,
                                        isFinal)
    return recover(data, signature)
