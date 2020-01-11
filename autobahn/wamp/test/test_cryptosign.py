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
import os
from unittest.mock import Mock

import txaio

if os.environ.get('USE_TWISTED', False):
    txaio.use_twisted()
elif os.environ.get('USE_ASYNCIO', False):
    txaio.use_asyncio()
else:
    raise Exception('no networking framework selected')

from autobahn.wamp.cryptosign import _makepad, HAS_CRYPTOSIGN
from autobahn.wamp import types
from autobahn.wamp.auth import create_authenticator

if HAS_CRYPTOSIGN:
    from autobahn.wamp.cryptosign import SigningKey
    from nacl.encoding import HexEncoder

import tempfile

import unittest

keybody = '''-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAa38i/4dNWFuZN/72QAJbyOwZvkUyML/u2b2B1uW4RbQAAAJj4FLyB+BS8
gQAAAAtzc2gtZWQyNTUxOQAAACAa38i/4dNWFuZN/72QAJbyOwZvkUyML/u2b2B1uW4RbQ
AAAEBNV9l6aPVVaWYgpthJwM5YJWhRjXKet1PcfHMt4oBFEBrfyL/h01YW5k3/vZAAlvI7
Bm+RTIwv+7ZvYHW5bhFtAAAAFXNvbWV1c2VyQGZ1bmt0aGF0LmNvbQ==
-----END OPENSSH PRIVATE KEY-----'''

pubkey = '''ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVp3hjHwIQyEladzd8mFcf0YSXcmyKS3qMLB7VqTQKm someuser@example.com
'''


@unittest.skipIf(not HAS_CRYPTOSIGN, 'nacl library not present')
class TestAuth(unittest.TestCase):

    def setUp(self):
        self.key = SigningKey.from_ssh_data(keybody)
        self.privkey_hex = self.key._key.encode(encoder=HexEncoder)
        m = hashlib.sha256()
        m.update("some TLS message".encode())
        self.channel_id = m.digest()

    def test_valid(self):
        session = Mock()
        session._transport.get_channel_id = Mock(return_value=self.channel_id)
        challenge = types.Challenge("ticket", dict(challenge="ff" * 32))
        signed = yield self.key.sign_challenge(session, challenge)
        self.assertEqual(
            '9b6f41540c9b95b4b7b281c3042fa9c54cef43c842d62ea3fd6030fcb66e70b3e80d49d44c29d1635da9348d02ec93f3ed1ef227dfb59a07b580095c2b82f80f9d16ca518aa0c2b707f2b2a609edeca73bca8dd59817a633f35574ac6fd80d00',
            signed.result,
        )

    def test_authenticator(self):
        authenticator = create_authenticator(
            "cryptosign",
            authid="someone",
            privkey=self.privkey_hex,
        )
        session = Mock()
        session._transport.get_channel_id = Mock(return_value=self.channel_id)
        challenge = types.Challenge("cryptosign", dict(challenge="ff" * 32))
        reply = yield authenticator.on_challenge(session, challenge)
        self.assertEqual(
            reply.result,
            '9b6f41540c9b95b4b7b281c3042fa9c54cef43c842d62ea3fd6030fcb66e70b3e80d49d44c29d1635da9348d02ec93f3ed1ef227dfb59a07b580095c2b82f80f9d16ca518aa0c2b707f2b2a609edeca73bca8dd59817a633f35574ac6fd80d00',
        )


class TestKey(unittest.TestCase):

    def test_pad(self):
        self.assertEqual(_makepad(0), '')
        self.assertEqual(_makepad(2), '\x01\x02')
        self.assertEqual(_makepad(3), '\x01\x02\x03')

    @unittest.skipIf(not HAS_CRYPTOSIGN, 'nacl library not present')
    def test_key(self):
        with tempfile.NamedTemporaryFile('w+t') as fp:
            fp.write(keybody)
            fp.seek(0)

            key = SigningKey.from_ssh_key(fp.name)
            self.assertEqual(key.public_key(), '1adfc8bfe1d35616e64dffbd900096f23b066f914c8c2ffbb66f6075b96e116d')

    @unittest.skipIf(not HAS_CRYPTOSIGN, 'nacl library not present')
    def test_pubkey(self):
        with tempfile.NamedTemporaryFile('w+t') as fp:
            fp.write(pubkey)
            fp.seek(0)

            key = SigningKey.from_ssh_key(fp.name)
            self.assertEqual(key.public_key(), '9569de18c7c0843212569dcddf2615c7f46125dc9b2292dea30b07b56a4d02a6')
            self.assertEqual(key.comment(), 'someuser@example.com')
