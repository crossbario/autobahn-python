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


def sign(eth_privkey, data):
    # FIXME: this fails on PyPy (but ot on CPy!) with
    #  Unknown format b'%M\xff\xcd2w\xc0\xb1f\x0fmB\xef\xbbuN\xda\xba\xbc+', attempted to normalize to 0x254dffcd3277c0b1660f6d42efbb754edababc2b
    _args = signing.sign_typed_data(data, eth_privkey)

    signature = signing.v_r_s_to_signature(*_args)
    assert len(signature) == _EIP712_SIG_LEN

    return signature


def recover(data, signature):
    assert type(signature) == bytes and len(signature) == _EIP712_SIG_LEN
    signer_address = signing.recover_typed_data(data, *signing.signature_to_v_r_s(signature))

    return a2b_hex(signer_address[2:])


def is_address(provided):
    return type(provided) == bytes and len(provided) == 20


def is_bytes16(provided):
    return type(provided) == bytes and len(provided) == 16
