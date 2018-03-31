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

from __future__ import absolute_import

import unittest2 as unittest
import platform

import six
import re
import json
import binascii
import hashlib
from mock import Mock

from autobahn.wamp import auth
from autobahn.wamp import types


# these test vectors are all for HMAC-SHA1
PBKDF2_TEST_VECTORS = [
    # From RFC 6070
    (b'password', b'salt', 1, 20, u'0c60c80f961f0e71f3a9b524af6012062fe037a6'),
    (b'password', b'salt', 2, 20, u'ea6c014dc72d6f8ccd1ed92ace1d41f0d8de8957'),

    # From Crypt-PBKDF2
    (b'password', b'ATHENA.MIT.EDUraeburn', 1, 16, u'cdedb5281bb2f801565a1122b2563515'),
    (b'password', b'ATHENA.MIT.EDUraeburn', 1, 32, u'cdedb5281bb2f801565a1122b25635150ad1f7a04bb9f3a333ecc0e2e1f70837'),
    (b'password', b'ATHENA.MIT.EDUraeburn', 2, 16, u'01dbee7f4a9e243e988b62c73cda935d'),
    (b'password', b'ATHENA.MIT.EDUraeburn', 2, 32, u'01dbee7f4a9e243e988b62c73cda935da05378b93244ec8f48a99e61ad799d86'),
    (b'password', b'ATHENA.MIT.EDUraeburn', 1200, 32, u'5c08eb61fdf71e4e4ec3cf6ba1f5512ba7e52ddbc5e5142f708a31e2e62b1e13'),
    (b'X' * 64, b'pass phrase equals block size', 1200, 32, u'139c30c0966bc32ba55fdbf212530ac9c5ec59f1a452f5cc9ad940fea0598ed1'),
    (b'X' * 65, b'pass phrase exceeds block size', 1200, 32, u'9ccad6d468770cd51b10e6a68721be611a8b4d282601db3b36be9246915ec82a'),
]

if platform.python_implementation() != 'PyPy':

    # the following fails on PyPy: "RuntimeError: maximum recursion depth exceeded"
    PBKDF2_TEST_VECTORS.extend(
        [
            # From RFC 6070
            (b'password', b'salt', 4096, 20, u'4b007901b765489abead49d926f721d065a429c1'),
            (b'passwordPASSWORDpassword', b'saltSALTsaltSALTsaltSALTsaltSALTsalt', 4096, 25, u'3d2eec4fe41c849b80c8d83662c0e44a8b291a964cf2f07038'),
            (b'pass\x00word', b'sa\x00lt', 4096, 16, u'56fa6aa75548099dcc37d7f03425e0c3'),

            # This one is from the RFC but it just takes for ages
            # (b'password', b'salt', 16777216, 20, u'eefe3d61cd4da4e4e9945b3d6ba2158c2634e984'),
        ]
    )


class TestWampAuthHelpers(unittest.TestCase):

    def test_pbkdf2(self):
        for tv in PBKDF2_TEST_VECTORS:
            result = auth.pbkdf2(tv[0], tv[1], tv[2], tv[3], hashlib.sha1)
            self.assertEqual(type(result), bytes)
            self.assertEqual(binascii.hexlify(result).decode('ascii'), tv[4])

    def test_generate_totp_secret_default(self):
        secret = auth.generate_totp_secret()
        self.assertEqual(type(secret), six.text_type)
        self.assertEqual(len(secret), 10 * 8 / 5)

    def test_generate_totp_secret_length(self):
        for length in [5, 10, 20, 30, 40, 50]:
            secret = auth.generate_totp_secret(length)
            self.assertEqual(type(secret), six.text_type)
            self.assertEqual(len(secret), length * 8 / 5)

    def test_compute_totp(self):
        pat = re.compile(u"\d{6}")
        secret = u"MFRGGZDFMZTWQ2LK"
        signature = auth.compute_totp(secret)
        self.assertEqual(type(signature), six.text_type)
        self.assertTrue(pat.match(signature) is not None)

    def test_compute_totp_offset(self):
        pat = re.compile(u"\d{6}")
        secret = u"MFRGGZDFMZTWQ2LK"
        for offset in range(-10, 10):
            signature = auth.compute_totp(secret, offset)
            self.assertEqual(type(signature), six.text_type)
            self.assertTrue(pat.match(signature) is not None)

    def test_derive_key(self):
        secret = u'L3L1YUE8Txlw'
        salt = u'salt123'
        key = auth.derive_key(secret.encode('utf8'), salt.encode('utf8'))
        self.assertEqual(type(key), bytes)
        self.assertEqual(key, b"qzcdsr9uu/L5hnss3kjNTRe490ETgA70ZBaB5rvnJ5Y=")

    def test_generate_wcs_default(self):
        secret = auth.generate_wcs()
        self.assertEqual(type(secret), bytes)
        self.assertEqual(len(secret), 14)

    def test_generate_wcs_length(self):
        for length in [5, 10, 20, 30, 40, 50]:
            secret = auth.generate_wcs(length)
            self.assertEqual(type(secret), bytes)
            self.assertEqual(len(secret), length)

    def test_compute_wcs(self):
        secret = u'L3L1YUE8Txlw'
        challenge = json.dumps([1, 2, 3], ensure_ascii=False).encode('utf8')
        signature = auth.compute_wcs(secret.encode('utf8'), challenge)
        self.assertEqual(type(signature), bytes)
        self.assertEqual(signature, b"1njQtmmeYO41N5EWEzD2kAjjEKRZ5kPZt/TzpYXOzR0=")


class TestScram(unittest.TestCase):

    def test_argon2id_static(self):
        # re-generate from the official argon2 tools:
        # echo -n "p4ssw0rd" | argon2 '1234567890abcdef' -id -t 32 -m 9 -p 1 -l 32
        expected = binascii.unhexlify('ee4a8acf9d5958354fb79a95ae20692d05e42591ba49fae85eb6700e8b0ed293')
        raw_hash = auth._hash_argon2id13_secret(
            b'p4ssw0rd',
            binascii.b2a_base64(b'1234567890abcdef'),  # ours takes base64-encoded salt
            32,  # this is WAY TOO SMALL; for production, use 4096 or higher
            512,  # note that the argon2 utility takes a "power of 2", so "-m 9" above == 512
        )
        decoded_hash = binascii.a2b_base64(raw_hash + b'==\n')
        self.assertEqual(expected, decoded_hash)

    def test_pbkdf2_static(self):
        expected = binascii.unhexlify('f6991a28c75f43751e0d75499fd7b8649f659118ddc1d61cee5883af547d15f5')
        # 8 iterations is WAY TOO FEW for production; this is a test
        raw_hash = auth._hash_pbkdf2_secret(b'p4ssw0rd', b'1234567890abcdef', 8)
        self.assertEqual(raw_hash, expected)

    def test_basic(self):
        scram = auth.AuthScram(
            nonce='1234567890abcdef',
            kdf='argon2id13',
            salt=binascii.b2a_hex(b'1234567890abcdef'),
            iterations=32,  # far too few; use 4096 or more for production
            memory=512,
            password=u'p4ssw0rd',
            authid=u'username',
        )
        # thought: if we could import crossbar code here, we could
        # test the "other side" of this with fewer mocks
        # (i.e. hard-coding the client nonce)
        scram._client_nonce = binascii.b2a_hex(b'1234567890abcdef').decode('ascii')
        self.assertEqual(
            {'nonce': u'31323334353637383930616263646566'},
            scram.authextra,
        )

        challenge = types.Challenge(u'scram', {
            'nonce': u'1234567890abcdeffedcba0987654321',
            'kdf': u'argon2id-13',
            'salt': binascii.b2a_hex(b'1234567890abcdef'),
            'iterations': 32,
            'memory': 512,
        })
        reply = scram.on_challenge(Mock(), challenge)
        self.assertEqual(
            b'f5r3loERzGVSuimE+lvO0bWna2zyswBo0HrZkaaEy38=',
            reply,
        )

        authextra = dict(
            scram_server_signature=b'f5r3loERzGVSuimE+lvO0bWna2zyswBo0HrZkaaEy38=',
        )
        scram.on_welcome(Mock(), authextra)

    def test_no_memory_arg(self):
        scram = auth.AuthScram(
            nonce='1234567890abcdef',
            kdf='argon2id13',
            salt=binascii.b2a_hex(b'1234567890abcdef'),
            iterations=4096,
            memory=512,
            password=u'p4ssw0rd',
            authid=u'username',
        )
        scram.authextra

        with self.assertRaises(ValueError) as ctx:
            challenge = types.Challenge(u'scram', {
                'nonce': u'1234567890abcdeffedcba0987654321',
                'kdf': u'argon2id-13',
                'salt': binascii.b2a_hex(b'1234567890abcdef'),
                'iterations': 4096,
                # no 'memory' key
            })
            scram.on_challenge(Mock(), challenge)
        self.assertIn(
            "requires 'memory' parameter",
            str(ctx.exception)
        )

    def test_unknown_arg(self):
        scram = auth.AuthScram(
            nonce='1234567890abcdef',
            kdf='argon2id13',
            salt=binascii.b2a_hex(b'1234567890abcdef'),
            iterations=4096,
            memory=512,
            password=u'p4ssw0rd',
            authid=u'username',
        )
        scram.authextra

        with self.assertRaises(RuntimeError) as ctx:
            challenge = types.Challenge(u'scram', {
                'nonce': u'1234567890abcdeffedcba0987654321',
                'kdf': u'argon2id-13',
                'salt': binascii.b2a_hex(b'1234567890abcdef'),
                'iterations': 4096,
                'memory': 512,
                'an_invalid_key': None
            })
            scram.on_challenge(Mock(), challenge)
        self.assertIn("an_invalid_key", str(ctx.exception))
