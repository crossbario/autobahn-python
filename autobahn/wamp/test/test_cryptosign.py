###############################################################################
#
# The MIT License (MIT)
#
# Copyright John-Mark Gurney
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

from __future__ import absolute_import

from autobahn.wamp.cryptosign import _makepad, HAS_CRYPTOSIGN

if HAS_CRYPTOSIGN:
    from autobahn.wamp.cryptosign import SigningKey

import tempfile

import unittest2 as unittest

keybody = '''-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAa38i/4dNWFuZN/72QAJbyOwZvkUyML/u2b2B1uW4RbQAAAJj4FLyB+BS8
gQAAAAtzc2gtZWQyNTUxOQAAACAa38i/4dNWFuZN/72QAJbyOwZvkUyML/u2b2B1uW4RbQ
AAAEBNV9l6aPVVaWYgpthJwM5YJWhRjXKet1PcfHMt4oBFEBrfyL/h01YW5k3/vZAAlvI7
Bm+RTIwv+7ZvYHW5bhFtAAAAFXNvbWV1c2VyQGZ1bmt0aGF0LmNvbQ==
-----END OPENSSH PRIVATE KEY-----
'''

pubkey = '''ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVp3hjHwIQyEladzd8mFcf0YSXcmyKS3qMLB7VqTQKm someuser@example.com
'''


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
