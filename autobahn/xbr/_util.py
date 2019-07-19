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

import click
from autobahn.xbr import XBR_DEBUG_NETWORK_ADDR

import eth_keys
from py_eth_sig_utils import signing

from crossbarfx.cfxdb import unpack_uint256, unpack_uint128

_EIP712_SIG_LEN = 32 + 32 + 1


def hl(text, bold=True, color='yellow'):
    if not isinstance(text, str):
        text = '{}'.format(text)
    return click.style(text, fg=color, bold=bold)


def _create_eip712_data(eth_adr, ed25519_pubkey, key_id, channel_seq, amount, balance):
    assert type(eth_adr) == bytes and len(eth_adr) == 20
    assert type(ed25519_pubkey) == bytes and len(ed25519_pubkey) == 32
    assert type(key_id) == bytes and len(key_id) == 16
    assert type(channel_seq) == int
    assert type(amount) == int
    assert type(balance) == int

    data = {
        'types': {
            'EIP712Domain': [
                {'name': 'name', 'type': 'string'},
                {'name': 'version', 'type': 'string'},
                {'name': 'chainId', 'type': 'uint256'},
                {'name': 'verifyingContract', 'type': 'address'},
            ],
            'Transaction': [
                # The delegate Ethereum address.
                {'name': 'adr', 'type': 'address'},

                # The delegate Ed25519 public key (32 bytes).
                {'name': 'pubkey', 'type': 'uint256'},

                # The UUID of the data encryption key (16 bytes).
                {'name': 'key_id', 'type': 'uint128'},

                # Channel off-chain transaction sequence number.
                {'name': 'channel_seq', 'type': 'uint32'},

                # Amount of the transaction.
                {'name': 'amount', 'type': 'uint256'},

                # Balance remaining in after the transaction.
                {'name': 'balance', 'type': 'uint256'},
            ],
        },
        'primaryType': 'Transaction',
        'domain': {
            'name': 'XBR',
            'version': '1',

            # test chain/network ID
            'chainId': 5777,

            # XBRNetwork contract address
            'verifyingContract': XBR_DEBUG_NETWORK_ADDR,
        },
        'message': {
            'adr': eth_adr,
            'pubkey': unpack_uint256(ed25519_pubkey),
            'key_id': unpack_uint128(key_id),
            'channel_seq': channel_seq,
            'amount': amount,
            'balance': balance,
        },
    }

    return data


def sign_eip712_data(eth_privkey, ed25519_pubkey, key_id, channel_seq, amount, balance):
    """

    :param buyer_adr: Ethereum address of buyer (a raw 20 bytes Ethereum address).
    :type buyer_adr: bytes

    :param buyer_pubkey: Public key of buyer (a raw 32 bytes Ed25519 public key).
    :type buyer_pubkey: bytes

    :param key_id: Unique ID of the key bought/sold (a UUID in raw 16 bytes)
    :type key_id: bytes

    :param channel_seq: Payment channel off-chain transaction sequence number.
    :type channel_seq: int

    :param amount: Amount paid/earned for the key.
    :type amount: int

    :param balance: Balance remaining in the payment/paying channel after buying/selling the key.
    :type balance: int

    :return: The signature according to EIP712 (32+32+1 raw bytes).
    :rtype: bytes
    """
    assert type(eth_privkey) == bytes and len(eth_privkey) == 32
    assert type(ed25519_pubkey) == bytes and len(ed25519_pubkey) == 32
    assert type(key_id) == bytes and len(key_id) == 16
    assert type(channel_seq) == int
    assert type(amount) == int
    assert type(balance) == int

    # make a private key object from the raw private key bytes
    pkey = eth_keys.keys.PrivateKey(eth_privkey)

    # get the canonical address of the account
    # eth_adr = web3.Web3.toChecksumAddress(pkey.public_key.to_canonical_address())
    eth_adr = pkey.public_key.to_canonical_address()

    # create EIP712 typed data object
    data = _create_eip712_data(eth_adr, ed25519_pubkey, key_id, channel_seq, amount, balance)

    signature = signing.v_r_s_to_signature(*signing.sign_typed_data(data, eth_privkey))
    assert len(signature) == _EIP712_SIG_LEN

    return signature


def recover_eip712_signer(eth_adr, ed25519_pubkey, key_id, channel_seq, amount, balance, signature):
    """
    Recover the signer address the given EIP712 signature was signed with.

    :param eth_adr: Input typed data for signature.
    :type eth_adr: bytes

    :param ed25519_pubkey: Input typed data for signature.
    :type ed25519_pubkey: bytes

    :param key_id: Input typed data for signature.
    :type key_id: bytes

    :param channel_seq: Input typed data for signature.
    :type channel_seq: int

    :param amount: Input typed data for signature.
    :type amount: int

    :param balance: Input typed data for signature.
    :type balance: int

    :param signature: The EIP712 signature to verify.
    :type signature: bytes

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    assert type(eth_adr) == bytes and len(eth_adr) == 20
    assert type(ed25519_pubkey) == bytes and len(ed25519_pubkey) == 32
    assert type(key_id) == bytes and len(key_id) == 16
    assert type(channel_seq) == int
    assert type(amount) == int
    assert type(balance) == int
    assert type(signature) == bytes and len(signature) == _EIP712_SIG_LEN

    # recreate EIP712 typed data object
    data = _create_eip712_data(eth_adr, ed25519_pubkey, key_id, channel_seq, amount, balance)

    # this returns the signer (checksummed) address as a string, eg "0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d"
    signer_address = signing.recover_typed_data(data, *signing.signature_to_v_r_s(signature))

    return a2b_hex(signer_address[2:])
