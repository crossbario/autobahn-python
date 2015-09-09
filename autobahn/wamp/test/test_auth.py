###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
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

import re
import six
import json
import binascii
import hashlib

from autobahn.wamp import auth, types
from autobahn.wamp.protocol import ApplicationSession

from mock import Mock

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
        self.assertEqual(type(secret), bytes)
        self.assertEqual(len(secret), 10 * 8 / 5)

    def test_generate_totp_secret_length(self):
        for length in [5, 10, 20, 30, 40, 50]:
            secret = auth.generate_totp_secret(length)
            self.assertEqual(type(secret), bytes)
            self.assertEqual(len(secret), length * 8 / 5)

    def test_compute_totp(self):
        pat = re.compile(b"\d{6}")
        secret = b"MFRGGZDFMZTWQ2LK"
        signature = auth.compute_totp(secret)
        self.assertEqual(type(signature), bytes)
        self.assertTrue(pat.match(signature) is not None)

    def test_compute_totp_offset(self):
        pat = re.compile(b"\d{6}")
        secret = b"MFRGGZDFMZTWQ2LK"
        for offset in range(-10, 10):
            signature = auth.compute_totp(secret, offset)
            self.assertEqual(type(signature), bytes)
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


class TestAuthOnChallenge(unittest.TestCase):
    """
    Tests for the default onChallenge implementation
    """

    def setUp(self):
        self.secret = b'cr0ssb4r'
        self.salt = u'salt123'
        self.config = dict(
            iterations=100,
            keylen=32,
        )
        self.salted_key = auth.derive_key(
            self.secret, self.salt.encode('utf8'), **self.config
        )
        # added after the derive_key so we can do ** trick above
        self.config['salt'] = self.salt

        # configure a session with the appropriate secret
        extra = {
            'wamp_cra': {
                'user': 'test_user',
                'secret': self.secret,
            }
        }
        self.session = ApplicationSession(
            types.ComponentConfig(realm=u"testing", extra=extra)
        )

    def test_success_onchallenge(self):
        extra = {
            "challenge": b"sign me",
        }
        extra.update(self.config)
        challenge = types.Challenge(u'wampcra', extra=extra)
        gold_signature = auth.compute_wcs(self.salted_key, b"sign me").decode('ascii')

        # pretend WAMP gave us a challenge to compute
        signature = self.session.onChallenge(challenge)

        self.assertTrue(isinstance(gold_signature, six.text_type))
        self.assertTrue(isinstance(signature, six.text_type))
        self.assertEqual(gold_signature, signature, "Signatures should match")

    def test_success_onconnect(self):
        self.session.join = Mock()

        self.session.onConnect()

        # we should have called through to join with
        # authmethods=['wampcra'] and an authid
        self.assertTrue(self.session.join.called, "we should have called .join()")
        args = self.session.join.call_args[0]
        kwargs = self.session.join.call_args[1]
        self.assertEqual(args, (self.session.config.realm,))
        self.assertTrue('authmethods' in kwargs)
        self.assertTrue('authid' in kwargs)
        self.assertTrue(u'wampcra' in kwargs['authmethods'])
        self.assertEqual('test_user', kwargs['authid'])

    def test_missing_secret(self):
        extra = {
            "challenge": b"sign me",
        }
        extra.update(self.config)
        challenge = types.Challenge(u'wampcra', extra=extra)
        # pretend user forgot the 'secret' key
        del self.session.config.extra['wamp_cra']['secret']

        self.assertRaises(Exception, self.session.onChallenge, challenge)

    def test_missing_user(self):
        # pretend user forgot the 'user' key
        del self.session.config.extra['wamp_cra']['user']

        # 'user' is only used in onConnect
        self.assertRaises(Exception, self.session.onConnect)

    def test_extra_not_a_dict(self):
        """
        if '.config.extra' is not a dict, we should not-fail
        """
        self.session.config.extra = object()
        self.session.join = Mock()

        self.session.onConnect()
        self.assertRaises(Exception, self.session.onChallenge, None)

        self.assertTrue(self.session.join.called, "we should have called .join()")
        self.assertEqual(None, self.session.join.call_args[1]['authid'])

    def test_no_wampcra_in_extra(self):
        self.session.config.extra = dict()  # no 'wamp_cra' key
        self.assertRaises(Exception, self.session.onChallenge, None)

    def test_wampcra_not_a_dict(self):
        self.session.config.extra = dict(wamp_cra=object())
        self.assertRaises(Exception, self.session.onChallenge, None)

    def test_wrong_iterations(self):
        extra = {
            "challenge": b"sign me",
            "salt": self.salt,
            "iterations": 42,
            "keylen": 32,
        }
        challenge = types.Challenge(u'wampcra', extra=extra)
        gold_signature = auth.compute_wcs(self.salted_key, b"sign me").decode('ascii')

        # pretend WAMP gave us a challenge to compute
        signature = self.session.onChallenge(challenge)

        self.assertTrue(isinstance(gold_signature, six.text_type))
        self.assertTrue(isinstance(signature, six.text_type))
        self.assertNotEqual(gold_signature, signature, "Signatures should NOT match")

    def test_wrong_keylen(self):
        extra = {
            "challenge": b"sign me",
            "salt": self.salt,
            "iterations": 100,
            "keylen": 8,
        }
        challenge = types.Challenge(u'wampcra', extra=extra)
        gold_signature = auth.compute_wcs(self.salted_key, b"sign me").decode('ascii')

        # pretend WAMP gave us a challenge to compute
        signature = self.session.onChallenge(challenge)

        self.assertTrue(isinstance(gold_signature, six.text_type))
        self.assertTrue(isinstance(signature, six.text_type))
        self.assertNotEqual(gold_signature, signature, "Signatures should NOT match")

    def test_unsalted_challenge(self):
        extra = {
            "challenge": b"sign me",
        }
        challenge = types.Challenge(u'wampcra', extra=extra)
        # using the secret directly, not .salted_key
        gold_signature = auth.compute_wcs(self.secret, b"sign me").decode('ascii')

        # pretend WAMP gave us a challenge to compute
        signature = self.session.onChallenge(challenge)

        self.assertTrue(isinstance(gold_signature, six.text_type))
        self.assertTrue(isinstance(signature, six.text_type))
        self.assertEqual(gold_signature, signature, "Signatures should match")
