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

import unittest
from binascii import a2b_hex

from autobahn.xbr import HAS_XBR

TESTVECTORS = [
    {
        'email': 'foobar@example.com',
        'password': 'secret123',
        'salt': None,
        'pkm': '5fa91eecfc1414db0db3cca9bfec64af495bdfa0bc8c135a8c17b6b5e3686cab',
        'contexts': {
            'wamp-cryptosign': '5c55e767c927e17e2a03a23ab46b516e41fb9e40377d2617104dd5622a9209cf',
        }
    },
    {
        'email': 'foobar@example.com',
        'password': 'secret123',
        'salt': a2b_hex('3761e806cda3c35d859c933d46e5d57b'),
        'pkm': 'c49556ca4c39dbfe147187b03b1dfcff7026d748cb27738a849a1cd5bfcf4bed',
        'contexts': {
            'wamp-cryptosign': '807af48521b1ecf4a7045814d75339159ecb157c1bffb00461edfebbaffcda71',
        }
    },
]

if HAS_XBR:
    from autobahn.xbr import stretch_argon2_secret, pkm_from_argon2_secret

    class TestXbrArgon2(unittest.TestCase):

        def test_stretch_argon2_secret(self):
            for tv in TESTVECTORS:
                email, password, salt = tv['email'], tv['password'], tv['salt']
                pkm = stretch_argon2_secret(email, password, salt=salt)
                self.assertEqual(pkm, a2b_hex(tv['pkm']))

        def test_pkm_from_argon2_secret(self):
            for tv in TESTVECTORS:
                email, password, salt = tv['email'], tv['password'], tv['salt']
                for context, expected_priv_key in tv['contexts'].items():
                    expected_priv_key = a2b_hex(expected_priv_key)
                    priv_key = pkm_from_argon2_secret(email=email, password=password, context=context, salt=salt)
                    self.assertEqual(priv_key, expected_priv_key)
