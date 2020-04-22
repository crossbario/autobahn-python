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


def _create_eip712_member_register(chainId: int, verifyingContract: bytes, member: bytes, registered: int,
                                   eula: str, profile: str) -> dict:
    """

    :param chainId:
    :param verifyingContract:
    :param member:
    :param registered:
    :param eula:
    :param profile:
    :return:
    """
    assert type(chainId) == int
    assert type(verifyingContract) == bytes and len(verifyingContract) == 20
    assert type(member) == bytes and len(member) == 20
    assert type(registered) == int
    assert type(eula) == str
    assert profile is None or type(profile) == str

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
            'EIP712MemberRegister': [
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
                    'name': 'registered',
                    'type': 'uint256'
                },
                {
                    'name': 'eula',
                    'type': 'string'
                },
                {
                    'name': 'profile',
                    'type': 'string'
                },
            ]
        },
        'primaryType': 'EIP712MemberRegister',
        'domain': {
            'name': 'XBR',
            'version': '1',
        },
        'message': {
            'chainId': chainId,
            'verifyingContract': verifyingContract,
            'member': member,
            'registered': registered,
            'eula': eula,
            'profile': profile or '',
        }
    }

    return data


def sign_eip712_member_register(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes,
                                registered: int, eula: str, profile: str) -> bytes:
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
    assert type(registered) == int
    assert type(eula) == str
    assert profile is None or type(profile) == str

    # make a private key object from the raw private key bytes
    # pkey = eth_keys.keys.PrivateKey(eth_privkey)

    # get the canonical address of the account
    # eth_adr = web3.Web3.toChecksumAddress(pkey.public_key.to_canonical_address())
    # eth_adr = pkey.public_key.to_canonical_address()

    # create EIP712 typed data object
    data = _create_eip712_member_register(chainId, verifyingContract, member, registered, eula, profile)

    # FIXME: this fails on PyPy (but ot on CPy!) with
    #  Unknown format b'%M\xff\xcd2w\xc0\xb1f\x0fmB\xef\xbbuN\xda\xba\xbc+', attempted to normalize to 0x254dffcd3277c0b1660f6d42efbb754edababc2b
    _args = signing.sign_typed_data(data, eth_privkey)

    signature = signing.v_r_s_to_signature(*_args)
    assert len(signature) == _EIP712_SIG_LEN

    return signature


def recover_eip712_member_register(chainId: int, verifyingContract: bytes, member: bytes, registered: int,
                                   eula: str, profile: str, signature: bytes) -> bytes:
    """
    Recover the signer address the given EIP712 signature was signed with.

    :return: The (computed) signer address the signature was signed with.
    :rtype: bytes
    """
    assert type(chainId) == int
    assert type(verifyingContract) == bytes and len(verifyingContract) == 20
    assert type(member) == bytes and len(member) == 20
    assert type(registered) == int
    assert type(eula) == str
    assert profile is None or type(profile) == str
    assert type(signature) == bytes and len(signature) == _EIP712_SIG_LEN

    # recreate EIP712 typed data object
    data = _create_eip712_member_register(chainId, verifyingContract, member, registered, eula, profile)

    # this returns the signer (checksummed) address as a string, eg "0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d"
    signer_address = signing.recover_typed_data(data, *signing.signature_to_v_r_s(signature))

    return a2b_hex(signer_address[2:])
