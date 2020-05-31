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

from typing import Optional
from ._eip712_base import sign, recover, _EIP712_SIG_LEN


def _create_eip712_node_pair(chainId: int, verifyingContract: bytes, member: bytes, paired: int,
                             nodeId: bytes, domainId: bytes, nodeType: int, nodeKey: bytes,
                             config: Optional[str]) -> dict:
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
    assert type(paired) == int
    assert type(nodeId) == bytes and len(nodeId) == 16
    assert type(domainId) == bytes and len(domainId) == 16
    assert type(nodeType) == int
    assert type(nodeKey) == bytes and len(nodeKey) == 32
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
            'config': config,
        }
    }

    return data


def sign_eip712_node_pair(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes, paired: int,
                          nodeId: bytes, domainId: bytes, nodeType: int, nodeKey: bytes,
                          config: Optional[str]) -> bytes:
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
    assert type(paired) == int
    assert type(nodeId) == bytes and len(nodeId) == 16
    assert type(domainId) == bytes and len(domainId) == 16
    assert type(nodeType) == int
    assert type(nodeKey) == bytes and len(nodeKey) == 32
    assert config is None or type(config) == str

    data = _create_eip712_node_pair(chainId, verifyingContract, member, paired, nodeId, domainId, nodeType,
                                    nodeKey, config)
    return sign(eth_privkey, data)


def recover_eip712_node_pair(chainId: int, verifyingContract: bytes, member: bytes, paired: int,
                             nodeId: bytes, domainId: bytes, nodeType: int, nodeKey: bytes,
                             config: str, signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    assert type(chainId) == int
    assert type(verifyingContract) == bytes and len(verifyingContract) == 20
    assert type(member) == bytes and len(member) == 20
    assert type(paired) == int
    assert type(nodeId) == bytes and len(nodeId) == 16
    assert type(domainId) == bytes and len(domainId) == 16
    assert type(nodeType) == int
    assert type(nodeKey) == bytes and len(nodeKey) == 32
    assert type(signature) == bytes and len(signature) == _EIP712_SIG_LEN

    data = _create_eip712_node_pair(chainId, verifyingContract, member, paired, nodeId, domainId, nodeType,
                                    nodeKey, config)
    return recover(data, signature)
