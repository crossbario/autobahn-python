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

import os
import unittest
from binascii import b2a_hex

from autobahn.util import (
    IdGenerator,
    generate_activation_code,
    generate_token,
    parse_activation_code,
)


class TestIdGenerator(unittest.TestCase):
    def test_idgenerator_is_generator(self):
        "IdGenerator follows the generator protocol"
        g = IdGenerator()
        self.assertEqual(1, next(g))
        self.assertEqual(2, next(g))

    def test_generator_wrap(self):
        g = IdGenerator()
        g._next = 2**53 - 1  # cheat a little

        v = next(g)
        self.assertEqual(v, 2**53)
        v = next(g)
        self.assertEqual(v, 1)

    def test_parse_valid_activation_codes(self):
        for i in range(20):
            code = generate_activation_code()
            parsed_code = parse_activation_code(code)
            self.assertTupleEqual(tuple(code.split("-")), parsed_code.groups())

    def test_parse_invalid_activation_codes(self):
        for i in range(20):
            code = b2a_hex(os.urandom(20)).decode()
            parsed_code = parse_activation_code(code)
            self.assertEqual(None, parsed_code)

    def test_generate_token(self):
        token = generate_token(5, 4)
        self.assertEqual(len(token), len("NUAG-UPQJ-MFGA-K5P5-MUGA"))
        self.assertEqual(len(token.split("-")), 5)
        for part in token.split("-"):
            self.assertEqual(len(part), 4)
