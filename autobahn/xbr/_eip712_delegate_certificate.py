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

from ._eip712_base import sign, recover, is_chain_id, is_address, is_bytes32, is_cs_pubkey, \
    is_block_number, is_signature, is_eth_privkey


def create_eip712_delegate_certificate(chainId: int,
                                       verifyingContract: bytes,
                                       validFrom: int,
                                       delegate: bytes,
                                       csPubKey: bytes,
                                       csChallenge: bytes,
                                       csChannelId: bytes,
                                       reservation: bytes) -> dict:
    """
    Delegate certificate: dynamic/one-time, off-chain.

    :param chainId:
    :param verifyingContract:
    :param validFrom:
    :param delegate:
    :param csPubKey:
    :param csChallenge:
    :param csChannelId:
    :param reservation:
    :return:
    """
    assert is_chain_id(chainId)
    assert is_address(verifyingContract)
    assert is_block_number(validFrom)
    assert is_address(delegate)
    assert is_cs_pubkey(csPubKey)
    assert is_bytes32(csChallenge)
    assert is_bytes32(csChannelId)
    assert is_address(reservation)

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
            'EIP712DelegateCertificate': [
                {
                    'name': 'chainId',
                    'type': 'uint256'
                },
                {
                    'name': 'verifyingContract',
                    'type': 'address'
                },
                {
                    'name': 'validFrom',
                    'type': 'uint256'
                },
                {
                    'name': 'delegate',
                    'type': 'address'
                },
                {
                    'name': 'csPubKey',
                    'type': 'bytes32'
                },
                {
                    'name': 'csChallenge',
                    'type': 'bytes32'
                },
                {
                    'name': 'csChannelId',
                    'type': 'bytes32'
                },
                {
                    'name': 'reservation',
                    'type': 'address'
                }
            ]
        },
        'primaryType': 'EIP712DelegateCertificate',
        'domain': {
            'name': 'WMP',
            'version': '1',
        },
        'message': {
            'chainId': chainId,
            'verifyingContract': verifyingContract,
            'validFrom': validFrom,
            'delegate': delegate,
            'csPubKey': csPubKey,
            'csChallenge': csChallenge,
            'csChannelId': csChannelId,
            'reservation': reservation,
        }
    }

    return data


def sign_eip712_delegate_certificate(eth_privkey: bytes,
                                     chainId: int,
                                     verifyingContract: bytes,
                                     validFrom: int,
                                     delegate: bytes,
                                     csPubKey: bytes,
                                     csChallenge: bytes,
                                     csChannelId: bytes,
                                     reservation: bytes) -> bytes:
    """
    Sign the given data using a EIP712 based signature with the provided private key.

    :param eth_privkey: Signing key.
    :param chainId:
    :param verifyingContract:
    :param validFrom:
    :param delegate:
    :param csPubKey:
    :param csChallenge:
    :param csChannelId:
    :param reservation:
    :return: The signature according to EIP712 (32+32+1 raw bytes).
    """
    assert is_eth_privkey(eth_privkey)

    data = create_eip712_delegate_certificate(chainId, verifyingContract, validFrom, delegate,
                                              csPubKey, csChallenge, csChannelId, reservation)
    return sign(eth_privkey, data)


def recover_eip712_delegate_certificate(chainId: int,
                                        verifyingContract: bytes,
                                        validFrom: int,
                                        delegate: bytes,
                                        csPubKey: bytes,
                                        csChallenge: bytes,
                                        csChannelId: bytes,
                                        reservation: bytes,
                                        signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :param chainId:
    :param verifyingContract:
    :param validFrom:
    :param delegate:
    :param csPubKey:
    :param csChallenge:
    :param csChannelId:
    :param reservation:
    :param signature:
    :return: The (computed) signer address the signature was signed with.
    """
    assert is_signature(signature)

    data = create_eip712_delegate_certificate(chainId, verifyingContract, validFrom, delegate,
                                              csPubKey, csChallenge, csChannelId, reservation)
    return recover(data, signature)
