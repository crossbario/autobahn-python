###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
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

import unittest
from binascii import a2b_hex

from autobahn.wamp.auth import derive_scram_credential

TEST_VECTORS = [
    {
        "email": "foobar@example.com",
        "password": "secret123",
        "salt": None,
        "expected": {
            "iterations": 4096,
            "kdf": "argon2id-13",
            "memory": 512,
            "salt": "3bc3ca01dd1d501ca1c22e1c5d7d16fe",
            "server-key": "8de7864c316f3c2356fd76cfdab696db55bc70e680fe5180e2f731e2345acca2",
            "stored-key": "e796c2f0a51770303ee4616bc630a66774d51a55003154aff2a54ec7c4ac0e38",
        },
    },
    {
        "email": "foobar@example.com",
        "password": "secret123",
        "salt": a2b_hex("ae1f0d2f422757809077785e660b62c6"),
        "expected": {
            "iterations": 4096,
            "kdf": "argon2id-13",
            "memory": 512,
            "salt": "ae1f0d2f422757809077785e660b62c6",
            "server-key": "0d8e7e9222a7c0e54c9e979aa342115699ff5696c45dc379b5ee241338a5861d",
            "stored-key": "5f19358ff6f38e267b6ef1ea1d862514ec4e8745a84682259fd3894be09febb5",
        },
    },
]


class TestKey(unittest.TestCase):
    def test_derive_scram_credential(self):
        for tv in TEST_VECTORS:
            email = tv["email"]
            password = tv["password"]
            salt = tv["salt"]
            expected = tv["expected"]
            credential = derive_scram_credential(email, password, salt)
            self.assertEqual(credential, expected)
