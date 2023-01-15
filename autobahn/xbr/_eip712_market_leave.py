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

from ._eip712_base import sign, recover, is_address, is_bytes16, is_block_number, \
    is_chain_id, is_eth_privkey, is_signature


def _create_eip712_market_leave(chainId: int, verifyingContract: bytes, member: bytes, left: int,
                                marketId: bytes, actorType: int) -> dict:
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
    assert is_chain_id(chainId)
    assert is_address(verifyingContract)
    assert is_address(member)
    assert is_block_number(left)
    assert is_bytes16(marketId)
    assert type(actorType) == int

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
            'EIP712MarketLeave': [
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
                    'name': 'left',
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
            ]
        },
        'primaryType': 'EIP712MarketLeave',
        'domain': {
            'name': 'XBR',
            'version': '1',
        },
        'message': {
            'chainId': chainId,
            'verifyingContract': verifyingContract,
            'member': member,
            'left': left,
            'marketId': marketId,
            'actorType': actorType,
        }
    }

    return data


def sign_eip712_market_leave(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes, left: int,
                             marketId: bytes, actorType: int) -> bytes:
    """

    :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
    :type eth_privkey: bytes

    :return: The signature according to EIP712 (32+32+1 raw bytes).
    :rtype: bytes
    """
    assert is_eth_privkey(eth_privkey)

    data = _create_eip712_market_leave(chainId, verifyingContract, member, left, marketId, actorType)

    return sign(eth_privkey, data)


def recover_eip712_market_leave(chainId: int, verifyingContract: bytes, member: bytes, left: int,
                                marketId: bytes, actorType: int, signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    assert is_signature(signature)

    data = _create_eip712_market_leave(chainId, verifyingContract, member, left, marketId, actorType)

    return recover(data, signature)
