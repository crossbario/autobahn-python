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

from autobahn.wamp.message import check_or_raise_realm_name, identity_realm_name_category
from autobahn.wamp.exception import InvalidUriError

import unittest


class TestWampIdentifiers(unittest.TestCase):

    def test_valid_realm_names(self):
        for name in [
            'realm1',
            'com.example.myapp1',
            'myapp1.example.com',
            'eth.wamp-proto',
            'wamp-proto.eth',
            'eth.wamp-proto.myapp1',
            'myapp1.wamp-proto.eth',
            'aaa',
            'Abc',
            'a00',
            'A00',
            '0x0000000000000000000000000000000000000000',
            '0xe59C7418403CF1D973485B36660728a5f4A8fF9c',
        ]:
            self.assertEqual(name, check_or_raise_realm_name(name))

    def test_invalid_realm_names(self):
        for name in [
            None,
            23,
            {},
            '',
            '.realm1',
            '123realm',
            '0x' + '00' * 64,
            '0x' + '00' * 32,
            '0x' + 'zz' * 40,
            'rlm$test',
            'a' * 256,
        ]:
            self.assertRaises(InvalidUriError, check_or_raise_realm_name, name)

    def test_realm_name_categories(self):
        for name, category in [
            # valid
            ('realm1', 'normal'),
            ('com.example.myapp1', 'normal'),
            ('myapp1.example.com', 'normal'),
            ('eth.wamp-proto', 'reverse_ens'),
            ('wamp-proto.eth', 'ens'),
            ('eth.wamp-proto.myapp1', 'reverse_ens'),
            ('myapp1.wamp-proto.eth', 'ens'),
            ('aaa', 'normal'),
            ('Abc', 'normal'),
            ('a00', 'normal'),
            ('A00', 'normal'),
            ('0x0000000000000000000000000000000000000000', 'eth'),
            ('0xe59C7418403CF1D973485B36660728a5f4A8fF9c', 'eth'),
            # invalid
            (None, None),
            (23, None),
            ({}, None),
            ('', None),
            ('.realm1', None),
            ('123realm', None),
            ('0x' + '00' * 64, None),
            ('0x' + '00' * 32, None),
            ('0x' + 'zz' * 40, None),
            ('rlm$test', None),
            ('a' * 256, None),
        ]:
            self.assertEqual(category, identity_realm_name_category(name))
