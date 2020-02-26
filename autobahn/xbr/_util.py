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
import web3
from py_eth_sig_utils import signing

_EIP712_SIG_LEN = 32 + 32 + 1


def make_w3(gateway_config):
    """
    Create a Web3 instance configured and ready-to-use gateway to the blockchain.

    :param gateway_config: Blockchain gateway configuration.
    :type gateway_config: dict

    :return: Configured Web3 instance.
    :rtype: :class:`web3.Web3`
    """
    request_kwargs = gateway_config.get('http_options', {})

    if gateway_config['type'] == 'auto':
        w3 = web3.Web3()

    elif gateway_config['type'] == 'user':
        w3 = web3.Web3(web3.Web3.HTTPProvider(gateway_config['http'], request_kwargs=request_kwargs))

    elif gateway_config['type'] == 'infura':
        project_id = gateway_config['key']
        # project_secret = gateway_config['secret']

        http_url = 'https://{}.infura.io/v3/{}'.format(gateway_config['network'], project_id)
        w3 = web3.Web3(web3.Web3.HTTPProvider(http_url, request_kwargs=request_kwargs))

        # https://web3py.readthedocs.io/en/stable/middleware.html#geth-style-proof-of-authority
        if gateway_config.get('network', None) == 'rinkeby':
            # This middleware is required to connect to geth --dev or the Rinkeby public network.
            from web3.middleware import geth_poa_middleware

            # inject the poa compatibility middleware to the innermost layer
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    else:
        raise RuntimeError('invalid blockchain gateway type "{}"'.format(gateway_config['type']))

    return w3


def unpack_uint128(data):
    assert data is None or type(data) == bytes, 'data must by bytes, was {}'.format(type(data))
    if data and type(data) == bytes:
        assert len(data) == 16, 'data must be bytes[16], but was bytes[{}]'.format(len(data))

    if data:
        return web3.Web3.toInt(data)
    else:
        return 0


def pack_uint128(value):
    assert value is None or (type(value) == int and value >= 0 and value < 2**128)

    if value:
        data = web3.Web3.toBytes(value)
        return b'\x00' * (16 - len(data)) + data
    else:
        return b'\x00' * 16


# FIXME: possibly use https://eth-abi.readthedocs.io/en/stable/decoding.html

def unpack_uint256(data):
    assert data is None or type(data) == bytes, 'data must by bytes, was {}'.format(type(data))
    if data and type(data) == bytes:
        assert len(data) == 32, 'data must be bytes[32], but was bytes[{}]'.format(len(data))

    if data:
        return int(web3.Web3.toInt(data))
    else:
        return 0


def pack_uint256(value):
    assert value is None or (type(value) == int and value >= 0 and value < 2**256), 'value must be uint256, but was {}'.format(value)

    if value:
        data = web3.Web3.toBytes(value)
        return b'\x00' * (32 - len(data)) + data
    else:
        return b'\x00' * 32


def hl(text, bold=True, color='yellow'):
    if not isinstance(text, str):
        text = '{}'.format(text)
    return click.style(text, fg=color, bold=bold)


def _create_eip712_data(verifying_adr, channel_adr, channel_seq, balance, is_final):
    assert type(verifying_adr) == bytes and len(verifying_adr) == 20
    assert type(channel_adr) == bytes and len(channel_adr) == 20
    assert type(channel_seq) == int
    assert type(balance) == int
    assert type(is_final) == bool

    data = {
        'types': {
            'EIP712Domain': [
                {'name': 'name', 'type': 'string'},
                {'name': 'version', 'type': 'string'},
                {'name': 'chainId', 'type': 'uint256'},
                {'name': 'verifyingContract', 'type': 'address'},
            ],
            'ChannelClose': [
                # The channel contract address.
                {'name': 'channel_adr', 'type': 'address'},

                # Channel off-chain transaction sequence number.
                {'name': 'channel_seq', 'type': 'uint32'},

                # Balance remaining in after the transaction.
                {'name': 'balance', 'type': 'uint256'},

                # Transaction is marked as final.
                {'name': 'is_final', 'type': 'bool'},
            ],
        },
        'primaryType': 'ChannelClose',
        'domain': {
            'name': 'XBR',
            'version': '1',
            'chainId': 1,
            'verifyingContract': verifying_adr,
        },
        'message': {
            'channel_adr': channel_adr,
            'channel_seq': channel_seq,
            'balance': balance,
            'is_final': is_final
        },
    }

    return data


def sign_eip712_data(eth_privkey, channel_adr, channel_seq, balance, is_final=False):
    """

    :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
    :type eth_privkey: bytes

    :param channel_adr: Channel contract address.
    :type channel_adr: bytes

    :param channel_seq: Payment channel off-chain transaction sequence number.
    :type channel_seq: int

    :param balance: Balance remaining in the payment/paying channel after buying/selling the key.
    :type balance: int

    :param is_final: Flag to indicate the transaction is considered final.
    :type is_final: bool

    :return: The signature according to EIP712 (32+32+1 raw bytes).
    :rtype: bytes
    """
    assert type(eth_privkey) == bytes and len(eth_privkey) == 32
    assert type(channel_adr) == bytes and len(channel_adr) == 20
    assert type(channel_seq) == int and channel_seq > 0
    assert type(balance) == int and balance >= 0
    assert type(is_final) == bool

    verifying_adr = a2b_hex('0x254dffcd3277C0b1660F6d42EFbB754edaBAbC2B'[2:])

    # make a private key object from the raw private key bytes
    # pkey = eth_keys.keys.PrivateKey(eth_privkey)

    # get the canonical address of the account
    # eth_adr = web3.Web3.toChecksumAddress(pkey.public_key.to_canonical_address())
    # eth_adr = pkey.public_key.to_canonical_address()

    # create EIP712 typed data object
    data = _create_eip712_data(verifying_adr, channel_adr, channel_seq, balance, is_final)

    # FIXME: this fails on PyPy (but ot on CPy!) with
    #  Unknown format b'%M\xff\xcd2w\xc0\xb1f\x0fmB\xef\xbbuN\xda\xba\xbc+', attempted to normalize to 0x254dffcd3277c0b1660f6d42efbb754edababc2b
    _args = signing.sign_typed_data(data, eth_privkey)

    signature = signing.v_r_s_to_signature(*_args)
    assert len(signature) == _EIP712_SIG_LEN

    return signature


def recover_eip712_signer(channel_adr, channel_seq, balance, is_final, signature):
    """
    Recover the signer address the given EIP712 signature was signed with.

    :param channel_adr: Channel contract address.
    :type channel_adr: bytes

    :param channel_seq: Payment channel off-chain transaction sequence number.
    :type channel_seq: int

    :param balance: Balance remaining in the payment/paying channel after buying/selling the key.
    :type balance: int

    :param is_final: Flag to indicate the transaction is considered final.
    :type is_final: bool

    :param signature: The EIP712 (32+32+1 raw bytes) signature to verify.
    :type signature: bytes

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    assert type(channel_adr) == bytes and len(channel_adr) == 20
    assert type(channel_seq) == int
    assert type(balance) == int
    assert type(is_final) == bool
    assert type(signature) == bytes and len(signature) == _EIP712_SIG_LEN

    verifying_adr = a2b_hex('0x254dffcd3277C0b1660F6d42EFbB754edaBAbC2B'[2:])

    # recreate EIP712 typed data object
    data = _create_eip712_data(verifying_adr, channel_adr, channel_seq, balance, is_final)

    # this returns the signer (checksummed) address as a string, eg "0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d"
    signer_address = signing.recover_typed_data(data, *signing.signature_to_v_r_s(signature))

    return a2b_hex(signer_address[2:])
