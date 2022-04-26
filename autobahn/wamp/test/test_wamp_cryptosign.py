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

import hashlib
import binascii
import unittest
from unittest.mock import Mock

import txaio
from autobahn.wamp.cryptosign import _makepad, HAS_CRYPTOSIGN
from autobahn.wamp import types
from autobahn.wamp.auth import create_authenticator

if HAS_CRYPTOSIGN:
    from autobahn.wamp.cryptosign import SigningKey
    from nacl.encoding import HexEncoder

import tempfile


keybody = '''-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAa38i/4dNWFuZN/72QAJbyOwZvkUyML/u2b2B1uW4RbQAAAJj4FLyB+BS8
gQAAAAtzc2gtZWQyNTUxOQAAACAa38i/4dNWFuZN/72QAJbyOwZvkUyML/u2b2B1uW4RbQ
AAAEBNV9l6aPVVaWYgpthJwM5YJWhRjXKet1PcfHMt4oBFEBrfyL/h01YW5k3/vZAAlvI7
Bm+RTIwv+7ZvYHW5bhFtAAAAFXNvbWV1c2VyQGZ1bmt0aGF0LmNvbQ==
-----END OPENSSH PRIVATE KEY-----'''

pubkey = '''ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVp3hjHwIQyEladzd8mFcf0YSXcmyKS3qMLB7VqTQKm someuser@example.com
'''

# test valid vectors for WAMP-cryptosign signature testing
testvectors = [
    {
        'priv_key': '4d57d97a68f555696620a6d849c0ce582568518d729eb753dc7c732de2804510',
        'challenge': 'ff' * 32,
        'signature': '9b6f41540c9b95b4b7b281c3042fa9c54cef43c842d62ea3fd6030fcb66e70b3e80d49d44c29d1635da9348d02ec93f3ed1ef227dfb59a07b580095c2b82f80f9d16ca518aa0c2b707f2b2a609edeca73bca8dd59817a633f35574ac6fd80d00'
    },
    {
        'priv_key': 'd511fe78e23934b3dadb52fcd022974b80bd92bccc7c5cf404e46cc0a8a2f5cd',
        'challenge': 'b26c1f87c13fc1da14997f1b5a71995dff8fbe0a62fae8473c7bdbd05bfb607d',
        'signature': '305aaa3ac25e98f651427688b3fc43fe7d8a68a7ec1d7d61c61517c519bd4a427c3015599d83ca28b4c652333920223844ef0725eb5dc2febfd6af7677b73f01d0852a29b460fc92ec943242ac638a053bbacc200512b18b30d15083cbdc9282'
    },
    {
        'priv_key': '6e1fde9cf9e2359a87420b65a87dc0c66136e66945196ba2475990d8a0c3a25b',
        'challenge': 'b05e6b8ad4d69abf74aa3be3c0ee40ae07d66e1895b9ab09285a2f1192d562d2',
        'signature': 'ee3c7644fd8070532bc1fde3d70d742267da545d8c8f03e63bda63f1ad4214f4d2c4bfdb4eb9526def42deeb7e31602a6ff99eba893e0a4ad4d45892ca75e608d2b75e24a189a7f78ca776ba36fc53f6c3e31c32f251f2c524f0a44202f2902d'
    }
]


class TestAuth(unittest.TestCase):

    def setUp(self):
        self.key = SigningKey.from_ssh_data(keybody)
        self.privkey_hex = self.key._key.encode(encoder=HexEncoder)
        m = hashlib.sha256()
        m.update("some TLS message".encode())
        channel_id = m.digest()
        self.transport_details = types.TransportDetails(channel_id={'tls-unique': channel_id})

    def test_public_key(self):
        self.assertEqual(self.key.public_key(binary=False), '1adfc8bfe1d35616e64dffbd900096f23b066f914c8c2ffbb66f6075b96e116d')

    def test_valid(self):
        session = Mock()
        session._transport.transport_details = self.transport_details

        challenge = types.Challenge("ticket", dict(challenge="ff" * 32))
        f_signed = self.key.sign_challenge(session, challenge)

        def success(signed):
            self.assertEqual(
                192,
                len(signed),
            )
            self.assertEqual(
                '9b6f41540c9b95b4b7b281c3042fa9c54cef43c842d62ea3fd6030fcb66e70b3e80d49d44c29d1635da9348d02ec93f3ed1ef227dfb59a07b580095c2b82f80f9d16ca518aa0c2b707f2b2a609edeca73bca8dd59817a633f35574ac6fd80d00',
                signed,
            )

        def failed(err):
            self.fail(str(err))

        txaio.add_callbacks(f_signed, success, failed)

    def test_testvectors(self):
        session = Mock()
        session._transport.transport_details = self.transport_details

        for testvec in testvectors:
            priv_key = SigningKey.from_key_bytes(binascii.a2b_hex(testvec['priv_key']))
            challenge = types.Challenge("ticket", dict(challenge=testvec['challenge']))
            f_signed = priv_key.sign_challenge(session, challenge)

            def success(signed):
                self.assertEqual(
                    192,
                    len(signed),
                )
                self.assertEqual(
                    testvec['signature'],
                    signed,
                )

            def failed(err):
                self.fail(str(err))

            txaio.add_callbacks(f_signed, success, failed)

    def test_authenticator(self):
        authenticator = create_authenticator(
            "cryptosign",
            authid="someone",
            privkey=self.privkey_hex,
        )
        session = Mock()
        session._transport.transport_details = self.transport_details
        challenge = types.Challenge("cryptosign", dict(challenge="ff" * 32))
        f_reply = authenticator.on_challenge(session, challenge)

        def success(reply):
            self.assertEqual(
                reply,
                '9b6f41540c9b95b4b7b281c3042fa9c54cef43c842d62ea3fd6030fcb66e70b3e80d49d44c29d1635da9348d02ec93f3ed1ef227dfb59a07b580095c2b82f80f9d16ca518aa0c2b707f2b2a609edeca73bca8dd59817a633f35574ac6fd80d00',
            )

        def failed(err):
            self.fail(str(err))

        txaio.add_callbacks(f_reply, success, failed)


class TestKey(unittest.TestCase):

    def test_pad(self):
        self.assertEqual(_makepad(0), b'')
        self.assertEqual(_makepad(2), b'\x01\x02')
        self.assertEqual(_makepad(3), b'\x01\x02\x03')
        self.assertEqual(_makepad(30), b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e')
        self.assertEqual(binascii.b2a_hex(_makepad(30)).decode(), '0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e')

    def test_key(self):
        with tempfile.NamedTemporaryFile('w+t') as fp:
            fp.write(keybody)
            fp.seek(0)

            key = SigningKey.from_ssh_key(fp.name)
            self.assertEqual(key.public_key(), '1adfc8bfe1d35616e64dffbd900096f23b066f914c8c2ffbb66f6075b96e116d')

    def test_pubkey(self):
        with tempfile.NamedTemporaryFile('w+t') as fp:
            fp.write(pubkey)
            fp.seek(0)

            key = SigningKey.from_ssh_key(fp.name)
            self.assertEqual(key.public_key(), '9569de18c7c0843212569dcddf2615c7f46125dc9b2292dea30b07b56a4d02a6')
            self.assertEqual(key.comment(), 'someuser@example.com')
