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

from typing import Optional
from ._eip712_base import sign, recover, is_chain_id, is_address, is_bytes16, is_cs_pubkey, \
    is_block_number, is_signature, is_eth_privkey


def _create_eip712_node_pair(chainId: int, verifyingContract: bytes, member: bytes, paired: int,
                             nodeId: bytes, domainId: bytes, nodeType: int, nodeKey: bytes,
                             amount: int, config: Optional[str]) -> dict:
    """

    :param chainId:
    :param verifyingContract:
    :param member:
    :param paired:
    :param nodeId:
    :param domainId:
    :param nodeKey:
    :param amount:
    :param config:
    :return:
    """
    assert is_chain_id(chainId)
    assert is_address(verifyingContract)
    assert is_address(member)
    assert is_block_number(paired)
    assert is_bytes16(nodeId)
    assert is_bytes16(domainId)
    assert type(nodeType) == int
    assert is_cs_pubkey(nodeKey)
    assert type(amount) == int
    assert config is None or type(config) == str

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
            'EIP712NodePair': [
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
                    'name': 'paired',
                    'type': 'uint256'
                },
                {
                    'name': 'nodeId',
                    'type': 'bytes16'
                },
                {
                    'name': 'domainId',
                    'type': 'bytes16'
                },
                {
                    'name': 'nodeType',
                    'type': 'uint8'
                },
                {
                    'name': 'nodeKey',
                    'type': 'bytes16'
                },
                {
                    'name': 'amount',
                    'type': 'uint256',
                },
                {
                    'name': 'config',
                    'type': 'string',
                },
            ]
        },
        'primaryType': 'EIP712NodePair',
        'domain': {
            'name': 'XBR',
            'version': '1',
        },
        'message': {
            'chainId': chainId,
            'verifyingContract': verifyingContract,
            'member': member,
            'paired': paired,
            'nodeId': nodeId,
            'domainId': domainId,
            'nodeType': nodeType,
            'nodeKey': nodeKey,
            'amount': amount,
            'config': config or '',
        }
    }

    return data


def sign_eip712_node_pair(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes, paired: int,
                          nodeId: bytes, domainId: bytes, nodeType: int, nodeKey: bytes,
                          amount: int, config: Optional[str]) -> bytes:
    """

    :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
    :type eth_privkey: bytes

    :return: The signature according to EIP712 (32+32+1 raw bytes).
    :rtype: bytes
    """
    assert is_eth_privkey(eth_privkey)

    data = _create_eip712_node_pair(chainId, verifyingContract, member, paired, nodeId, domainId, nodeType,
                                    nodeKey, amount, config)
    return sign(eth_privkey, data)


def recover_eip712_node_pair(chainId: int, verifyingContract: bytes, member: bytes, paired: int,
                             nodeId: bytes, domainId: bytes, nodeType: int, nodeKey: bytes,
                             amount: int, config: str, signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    assert is_signature(signature)

    data = _create_eip712_node_pair(chainId, verifyingContract, member, paired, nodeId, domainId, nodeType,
                                    nodeKey, amount, config)
    return recover(data, signature)
