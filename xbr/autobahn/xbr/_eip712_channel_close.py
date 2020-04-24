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
    assert type(chainId) == int
    assert type(verifyingContract) == bytes and len(verifyingContract) == 20
    assert type(closeAt) == int
    assert type(marketId) == bytes and len(marketId) == 16
    assert type(channelId) == bytes and len(channelId) == 16
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
    # create EIP712 typed data object
    data = _create_eip712_channel_close(chainId, verifyingContract, closeAt, marketId, channelId, channelSeq, balance,
                                        isFinal)

    # FIXME: this fails on PyPy (but ot on CPy!) with
    #  Unknown format b'%M\xff\xcd2w\xc0\xb1f\x0fmB\xef\xbbuN\xda\xba\xbc+', attempted to normalize to 0x254dffcd3277c0b1660f6d42efbb754edababc2b
    _args = signing.sign_typed_data(data, eth_privkey)

    signature = signing.v_r_s_to_signature(*_args)
    assert len(signature) == _EIP712_SIG_LEN

    return signature


def recover_eip712_channel_close(chainId: int, verifyingContract: bytes, closeAt: int, marketId: bytes, channelId: bytes,
                                 channelSeq: int, balance: int, isFinal: bool, signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    # create EIP712 typed data object
    data = _create_eip712_channel_close(chainId, verifyingContract, closeAt, marketId, channelId, channelSeq, balance,
                                        isFinal)

    assert type(signature) == bytes and len(signature) == _EIP712_SIG_LEN
    signer_address = signing.recover_typed_data(data, *signing.signature_to_v_r_s(signature))

    return a2b_hex(signer_address[2:])
