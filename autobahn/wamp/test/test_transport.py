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

from autobahn.wamp.connection import check_transport, check_endpoint


class TestTransportParsing(unittest.TestCase):

    def test_invalid_key(self):
        self.assertRaises(Exception, check_transport, {"foo": "bar"})

    def test_invalid_type(self):
        self.assertRaises(Exception, check_transport, {"type": "invalid"})

    def test_rawsocket(self):
        self.assertRaises(RuntimeError, check_transport,
                          {
                              "type": "rawsocket",
                          })

    def test_websocket_valid(self):
        self.assertTrue(
            check_transport(
                {
                    "type": "websocket",
                    "url": u"ws://127.0.0.1/ws",
                }
            )
        )

    def test_websocket_no_url(self):
        self.assertRaises(Exception, check_transport,
                          {
                              "type": "websocket",
                          })

    def test_websocket_secure_but_ws(self):
        self.assertRaises(Exception, check_transport,
                          {
                              "type": "websocket",
                              "url": u"ws://127.0.0.1/ws",
                              "endpoint": {
                                  "tls": True,
                              }
                          })

    def test_valid(self):
        self.assertTrue(
            check_transport(
                {
                    "type": "websocket",
                    "url": u"ws://127.0.0.1/ws",
                    "endpoint": {
                        "host": "127.0.0.1",
                        "port": 1234,
                    }
                }
            )
        )

    def test_(self):
        self.assertRaises(Exception, check_transport, {"type": "websocket"})


class TestEndpointParsing(unittest.TestCase):

    def test_invalid_key(self):
        self.assertRaises(
            Exception, check_endpoint,
            {
                "invalid": "key",
            }
        )

    def test_invalid_kind(self):
        self.assertRaises(
            Exception, check_endpoint,
            {
                "type": "something_strange",
            }
        )

    def test_tcp_invalid_keys(self):
        self.assertRaises(
            Exception, check_endpoint,
            {
                "type": "tcp",
                "path": "foo",
            }
        )

    def test_tcp_no_host(self):
        self.assertRaises(
            Exception, check_endpoint,
            {
                "type": "tcp",
            }
        )

    def test_tcp_invalid_version(self):
        self.assertRaises(
            Exception, check_endpoint,
            {
                "version": 1,
                "host": "127.0.0.1",
            }
        )

    def test_unix_invalid_keys(self):
        for bad_key in ['host', 'port', 'interface', 'tls', 'shared', 'version']:
            self.assertRaises(
                Exception, check_endpoint,
                {
                    "type": "unix",
                    bad_key: "value",
                }
            )

    def test_unix_no_path(self):
        self.assertRaises(
            Exception, check_endpoint,
            {
                "type": "unix",
            }
        )

    def test_unix_valid(self):
        self.assertTrue(
            check_endpoint(
                {
                    "type": "unix",
                    "path": "/tmp/foo",
                }
            )
        )

    def test_timeout(self):
        self.assertTrue(
            check_endpoint(
                {
                    "type": "tcp",
                    "host": "127.0.0.1",
                    "port": 1234,
                    "timeout": 123.456,
                }
            )
        )

    def test_negative_timeout(self):
        self.assertRaises(
            Exception,
            check_endpoint,
            {
                "type": "tcp",
                "host": "127.0.0.1",
                "port": 1234,
                "timeout": -123.456,
            }
        )

    def test_bad_connecting_keys(self):
        for bad_key in ['backlog', 'shared', 'interface']:
            self.assertRaises(
                Exception,
                check_endpoint,
                {
                    "type": "tcp",
                    "host": "127.0.0.1",
                    bad_key: "value",
                }
            )
