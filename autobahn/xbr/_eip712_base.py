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

from typing import Dict, Any
from binascii import a2b_hex
from py_eth_sig_utils import signing

_EIP712_SIG_LEN = 32 + 32 + 1


def _hash(data) -> bytes:
    """
    keccak256(abi.encode(
            EIP712_MEMBER_REGISTER_TYPEHASH,
            obj.chainId,
            obj.verifyingContract,
            obj.member,
            obj.registered,
            keccak256(bytes(obj.eula)),
            keccak256(bytes(obj.profile))
        ));

    :param data:
    :return:
    """


def sign(eth_privkey: bytes, data: Dict[str, Any]) -> bytes:
    """
    Sign the given data using the given Ethereum private key.

    :param eth_privkey: Signing key.
    :param data: Data to sign.
    :return: Signature.
    """
    # internally, this is using py_eth_sig_utils.eip712.encode_typed_data
    _args = signing.sign_typed_data(data, eth_privkey)

    # serialize structured signature (v, r, s) into bytes
    signature = signing.v_r_s_to_signature(*_args)

    # be paranoid about what to expect
    assert type(signature) == bytes and len(signature) == _EIP712_SIG_LEN

    return signature


def recover(data: Dict[str, Any], signature: bytes) -> bytes:
    """
    Recover the Ethereum address of the signer, given the data and signature.

    :param data: Signed data.
    :param signature: Signature.
    :return: Signing address.
    """
    assert type(signature) == bytes and len(signature) == _EIP712_SIG_LEN
    signer_address = signing.recover_typed_data(data, *signing.signature_to_v_r_s(signature))

    return a2b_hex(signer_address[2:])


def is_address(provided: Any) -> bool:
    """
    Check if the value is a proper Ethereum address.

    :param provided: The value to check.
    :return: True iff the value is of correct type.
    """
    return type(provided) == bytes and len(provided) == 20


def is_bytes16(provided: Any) -> bool:
    """
    Check if the value is a proper (binary) UUID.

    :param provided: The value to check.
    :return: True iff the value is of correct type.
    """
    return type(provided) == bytes and len(provided) == 16


def is_bytes32(provided: Any) -> bool:
    """
    Check if the value is of type bytes and length 32.

    :param provided: The value to check.
    :return: True iff the value is of correct type.
    """
    return type(provided) == bytes and len(provided) == 32


def is_signature(provided: Any) -> bool:
    """
    Check if the value is a proper Ethereum signature.

    :param provided: The value to check.
    :return: True iff the value is of correct type.
    """
    return type(provided) == bytes and len(provided) == _EIP712_SIG_LEN


def is_eth_privkey(provided: Any) -> bool:
    """
    Check if the value is a proper Ethereum private key (seed).

    :param provided: The value to check.
    :return: True iff the value is of correct type.
    """
    return type(provided) == bytes and len(provided) == 32


def is_cs_pubkey(provided: Any) -> bool:
    """
    Check if the value is a proper WAMP-cryptosign public key.

    :param provided: The value to check.
    :return: True iff the value is of correct type.
    """
    return type(provided) == bytes and len(provided) == 32


def is_block_number(provided: Any) -> bool:
    """
    Check if the value is a proper Ethereum block number.

    :param provided: The value to check.
    :return: True iff the value is of correct type.
    """
    return type(provided) == int


def is_chain_id(provided: Any) -> bool:
    """
    Check if the value is a proper Ethereum chain ID.

    :param provided: The value to check.
    :return: True iff the value is of correct type.
    """
    # here is a list of public networks: https://chainid.network/
    # note: we allow any positive integer to account for private networks
    return type(provided) == int and provided > 0
