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

from ._eip712_base import sign, recover, is_address, is_eth_privkey, \
    is_signature, is_cs_pubkey


def _create_eip712_market_member_login(member: bytes, client_pubkey: bytes) -> dict:
    assert is_address(member)
    assert is_cs_pubkey(client_pubkey)

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
            'EIP712MarketMemberLogin': [
                {
                    'name': 'member',
                    'type': 'address'
                },
                {
                    'name': 'client_pubkey',
                    'type': 'bytes32',
                },
            ]
        },
        'primaryType': 'EIP712MarketMemberLogin',
        'domain': {
            'name': 'XBR',
            'version': '1',
        },
        'message': {
            'member': member,
            'client_pubkey': client_pubkey,
        }
    }

    return data


def sign_eip712_market_member_login(eth_privkey: bytes, member: bytes, client_pubkey: bytes) -> bytes:
    assert is_eth_privkey(eth_privkey)

    data = _create_eip712_market_member_login(member, client_pubkey)

    return sign(eth_privkey, data)


def recover_eip712_market_member_login(member: bytes, client_pubkey: bytes, signature: bytes) -> bytes:
    assert is_signature(signature)

    data = _create_eip712_market_member_login(member, client_pubkey)

    return recover(data, signature)
