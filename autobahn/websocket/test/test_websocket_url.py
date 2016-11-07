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

from autobahn.websocket.util import create_url, parse_url


class TestCreateWsUrl(unittest.TestCase):

    def test_create_url01(self):
        self.assertEqual(create_url("localhost"), "ws://localhost:80/")

    def test_create_url02(self):
        self.assertEqual(create_url("localhost", port=8090), "ws://localhost:8090/")

    def test_create_url03(self):
        self.assertEqual(create_url("localhost", path="ws"), "ws://localhost:80/ws")

    def test_create_url04(self):
        self.assertEqual(create_url("localhost", path="/ws"), "ws://localhost:80/ws")

    def test_create_url05(self):
        self.assertEqual(create_url("localhost", path="/ws/foobar"), "ws://localhost:80/ws/foobar")

    def test_create_url06(self):
        self.assertEqual(create_url("localhost", isSecure=True), "wss://localhost:443/")

    def test_create_url07(self):
        self.assertEqual(create_url("localhost", isSecure=True, port=443), "wss://localhost:443/")

    def test_create_url08(self):
        self.assertEqual(create_url("localhost", isSecure=True, port=80), "wss://localhost:80/")

    def test_create_url09(self):
        self.assertEqual(create_url("localhost", isSecure=True, port=9090, path="ws", params={'foo': 'bar'}), "wss://localhost:9090/ws?foo=bar")

    def test_create_url10(self):
        wsurl = create_url("localhost", isSecure=True, port=9090, path="ws", params={'foo': 'bar', 'moo': 23})
        self.assertTrue(wsurl == "wss://localhost:9090/ws?foo=bar&moo=23" or wsurl == "wss://localhost:9090/ws?moo=23&foo=bar")

    def test_create_url11(self):
        self.assertEqual(create_url("127.0.0.1", path="ws"), "ws://127.0.0.1:80/ws")

    def test_create_url12(self):
        self.assertEqual(create_url("62.146.25.34", path="ws"), "ws://62.146.25.34:80/ws")

    def test_create_url13(self):
        self.assertEqual(create_url("subsub1.sub1.something.com", path="ws"), "ws://subsub1.sub1.something.com:80/ws")

    def test_create_url14(self):
        self.assertEqual(create_url("::1", path="ws"), "ws://::1:80/ws")

    def test_create_url15(self):
        self.assertEqual(create_url("0:0:0:0:0:0:0:1", path="ws"), "ws://0:0:0:0:0:0:0:1:80/ws")


class TestParseWsUrl(unittest.TestCase):

    # parse_url -> (isSecure, host, port, resource, path, params)

    def test_parse_url01(self):
        self.assertEqual(parse_url("ws://localhost"), (False, 'localhost', 80, '/', '/', {}))

    def test_parse_url02(self):
        self.assertEqual(parse_url("ws://localhost:80"), (False, 'localhost', 80, '/', '/', {}))

    def test_parse_url03(self):
        self.assertEqual(parse_url("wss://localhost"), (True, 'localhost', 443, '/', '/', {}))

    def test_parse_url04(self):
        self.assertEqual(parse_url("wss://localhost:443"), (True, 'localhost', 443, '/', '/', {}))

    def test_parse_url05(self):
        self.assertEqual(parse_url("wss://localhost/ws"), (True, 'localhost', 443, '/ws', '/ws', {}))

    def test_parse_url06(self):
        self.assertEqual(parse_url("wss://localhost/ws?foo=bar"), (True, 'localhost', 443, '/ws?foo=bar', '/ws', {'foo': ['bar']}))

    def test_parse_url07(self):
        self.assertEqual(parse_url("wss://localhost/ws?foo=bar&moo=23"), (True, 'localhost', 443, '/ws?foo=bar&moo=23', '/ws', {'moo': ['23'], 'foo': ['bar']}))

    def test_parse_url08(self):
        self.assertEqual(parse_url("wss://localhost/ws?foo=bar&moo=23&moo=44"), (True, 'localhost', 443, '/ws?foo=bar&moo=23&moo=44', '/ws', {'moo': ['23', '44'], 'foo': ['bar']}))

    def test_parse_url09(self):
        self.assertRaises(Exception, parse_url, "http://localhost")

    def test_parse_url10(self):
        self.assertRaises(Exception, parse_url, "https://localhost")

    def test_parse_url11(self):
        self.assertRaises(Exception, parse_url, "http://localhost:80")

    def test_parse_url12(self):
        self.assertRaises(Exception, parse_url, "http://localhost#frag1")

    def test_parse_url13(self):
        self.assertRaises(Exception, parse_url, "wss://")

    def test_parse_url14(self):
        self.assertRaises(Exception, parse_url, "ws://")
