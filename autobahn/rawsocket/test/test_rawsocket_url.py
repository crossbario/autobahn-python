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

from autobahn.rawsocket.util import create_url, parse_url


class TestCreateRsUrl(unittest.TestCase):

    def test_create_url01(self):
        self.assertEqual(create_url("localhost"), "rs://localhost:80")

    def test_create_url02(self):
        self.assertEqual(create_url("localhost", port=8090), "rs://localhost:8090")

    def test_create_url03(self):
        self.assertEqual(create_url("localhost", isSecure=True), "rss://localhost:443")

    def test_create_url04(self):
        self.assertEqual(create_url("localhost", isSecure=True, port=443), "rss://localhost:443")

    def test_create_url05(self):
        self.assertEqual(create_url("localhost", isSecure=True, port=80), "rss://localhost:80")

    def test_create_url06(self):
        self.assertEqual(create_url("unix", port="file.sock"), "rs://unix:file.sock")

    def test_create_url07(self):
        self.assertEqual(create_url("unix", port="/tmp/file.sock"), "rs://unix:/tmp/file.sock")

    def test_create_url08(self):
        self.assertEqual(create_url("unix", port="../file.sock"), "rs://unix:../file.sock")

    def test_create_url09(self):
        self.assertEqual(create_url("unix", isSecure=True, port="file.sock"), "rss://unix:file.sock")

    def test_create_url10(self):
        self.assertEqual(create_url("unix", isSecure=True, port="/tmp/file.sock"), "rss://unix:/tmp/file.sock")

    def test_create_url11(self):
        self.assertEqual(create_url("unix", isSecure=True, port="../file.sock"), "rss://unix:../file.sock")


class TestParseWsUrl(unittest.TestCase):

    # parse_url -> (isSecure, host, port)

    def test_parse_url01(self):
        self.assertEqual(parse_url("rs://localhost"), (False, 'localhost', 80))

    def test_parse_url02(self):
        self.assertEqual(parse_url("rss://localhost"), (True, 'localhost', 443))

    def test_parse_url03(self):
        self.assertEqual(parse_url("rs://localhost:9000"), (False, 'localhost', 9000))

    def test_parse_url04(self):
        self.assertEqual(parse_url("rss://localhost:9000"), (True, 'localhost', 9000))

    def test_parse_url05(self):
        self.assertRaises(Exception, parse_url, "ws://localhost")

    def test_parse_url06(self):
        self.assertRaises(Exception, parse_url, "wss://localhost")

    def test_parse_url07(self):
        self.assertRaises(Exception, parse_url, "ws://localhost:80")

    def test_parse_url08(self):
        self.assertRaises(Exception, parse_url, "rs://localhost/somepath")

    def test_parse_url09(self):
        self.assertRaises(Exception, parse_url, "rs://localhost#somefrag")

    def test_parse_url10(self):
        self.assertRaises(Exception, parse_url, "rs://localhost?foo=bar")

    def test_parse_url11(self):
        self.assertRaises(Exception, parse_url, "rss://")

    def test_parse_url12(self):
        self.assertRaises(Exception, parse_url, "rs://")

    def test_parse_url13(self):
        self.assertEqual(parse_url("rs://unix:file.sock"), (False, 'unix', 'file.sock'))

    def test_parse_url14(self):
        self.assertEqual(parse_url("rs://unix:/tmp/file.sock"), (False, 'unix', '/tmp/file.sock'))

    def test_parse_url15(self):
        self.assertEqual(parse_url("rs://unix:../file.sock"), (False, 'unix', '../file.sock'))

    def test_parse_url16(self):
        self.assertEqual(parse_url("rss://unix:file.sock"), (True, 'unix', 'file.sock'))

    def test_parse_url17(self):
        self.assertEqual(parse_url("rss://unix:/tmp/file.sock"), (True, 'unix', '/tmp/file.sock'))

    def test_parse_url18(self):
        self.assertEqual(parse_url("rss://unix:../file.sock"), (True, 'unix', '../file.sock'))
