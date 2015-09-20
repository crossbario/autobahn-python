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

import os
import unittest2 as unittest
from mock import patch

from autobahn.wamp import transport


class TestTransportParsing(unittest.TestCase):

    def test_invalid_key(self):
        self.assertRaises(Exception, transport.check, {"foo": "bar"})

    def test_invalid_type(self):
        self.assertRaises(Exception, transport.check, {"type": "invalid"})

    def test_rawsocket(self):
        self.assertRaises(RuntimeError, transport.check,
                          {
                              "type": "rawsocket",
                          })

    def test_websocket_valid(self):
        self.assertTrue(
            transport.check(
                {
                    "type": "websocket",
                    "url": u"ws://127.0.0.1/ws",
                }
            )
        )

    def test_websocket_no_url(self):
        self.assertRaises(Exception, transport.check,
                          {
                              "type": "websocket",
                          })

    def test_websocket_secure_but_ws(self):
        self.assertRaises(Exception, transport.check,
                          {
                              "type": "websocket",
                              "url": u"ws://127.0.0.1/ws",
                              "endpoint": {
                                  "tls": True,
                              }
                          })

    def test_valid(self):
        self.assertTrue(
            transport.check(
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
        self.assertRaises(Exception, transport.check, {"type": "websocket"})


class TestEndpointParsing(unittest.TestCase):

    def test_invalid_key(self):
        self.assertRaises(
            Exception, transport.check_endpoint,
            {
                "invalid": "key",
            }
        )

    def test_invalid_kind(self):
        self.assertRaises(
            Exception, transport.check_endpoint,
            {
                "type": "something_strange",
            }
        )

    def test_tcp_invalid_keys(self):
        self.assertRaises(
            Exception, transport.check_endpoint,
            {
                "type": "tcp",
                "path": "foo",
            }
        )

    def test_tcp_no_host(self):
        self.assertRaises(
            Exception, transport.check_endpoint,
            {
                "type": "tcp",
            }
        )

    def test_tcp_interface(self):
        self.assertRaises(
            Exception, transport.check_endpoint,
            {
                "type": "tcp",
                "host": "tavendo.de",
                "interface": "eth0",
            }
        )

    def test_tcp_listen(self):
        self.assertTrue(
            transport.check_endpoint(
                {
                    "type": "tcp",
                    "host": "tavendo.de",
                    "interface": "eth0",
                },
                listen=True,
            )
        )

    def test_tcp_invalid_version(self):
        self.assertRaises(
            Exception, transport.check_endpoint,
            {
                "version": 1,
                "host": "127.0.0.1",
            }
        )

    def test_unix_invalid_keys(self):
        for bad_key in ['host', 'port', 'interface', 'tls', 'shared', 'version']:
            self.assertRaises(
                Exception, transport.check_endpoint,
                {
                    "type": "unix",
                    bad_key: "value",
                }
            )

    def test_unix_no_path(self):
        self.assertRaises(
            Exception, transport.check_endpoint,
            {
                "type": "unix",
            }
        )

    def test_unix_valid(self):
        self.assertTrue(
            transport.check_endpoint(
                {
                    "type": "unix",
                    "path": "/tmp/foo",
                }
            )
        )

    def test_timeout(self):
        self.assertTrue(
            transport.check_endpoint(
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
            transport.check_endpoint,
            {
                "type": "tcp",
                "host": "127.0.0.1",
                "port": 1234,
                "timeout": -123.456,
            }
        )

    def test_listening_timeout(self):
        self.assertRaises(
            Exception,
            transport.check_endpoint,
            {
                "type": "tcp",
                "host": "127.0.0.1",
                "port": 1234,
                "timeout": 123.456,
                "backlog": 10,
                "interface": "eth0",
            },
            listen=True,
        )

    def test_bad_connecting_keys(self):
        for bad_key in ['backlog', 'shared', 'interface']:
            self.assertRaises(
                Exception,
                transport.check_endpoint,
                {
                    "type": "tcp",
                    "host": "127.0.0.1",
                    bad_key: "value",
                }
            )


if os.environ.get('USE_TWISTED', False):
    from twisted.trial import unittest
    from twisted.internet.endpoints import serverFromString, clientFromString
    from twisted.internet import reactor

    class TestEndpointTwistedObjects(unittest.TestCase):
        """
        Confirms we can pass real Twisted objects into check_endpoint
        """
        def test_endpoint_string_client(self):
            with patch('autobahn.wamp.transport.clientFromString') as cfs:
                self.assertTrue(transport.check_endpoint("tcp:host=localhost:port=1234"))
                self.assertTrue(cfs.mock_called)

        def test_endpoint_string_client_invalid(self):
            # bonus points if we mock clientFromString to raise
            # instead of depending on badparser being a bad plugin name?
            self.assertFalse(transport.check_endpoint("badparser:foo=bar"))

        def test_endpoint_string_server(self):
            with patch('autobahn.wamp.transport.serverFromString') as sfs:
                self.assertTrue(transport.check_endpoint("tcp:host=localhost:port=1234", listen=True))
                self.assertTrue(sfs.mock_called)

        def test_istream_client(self):
            ep = clientFromString(reactor, "tcp:host=127.0.0.1:port=1234")
            self.assertTrue(transport.check_endpoint(ep))

        def test_istream_client_but_listening(self):
            ep = clientFromString(reactor, "tcp:host=127.0.0.1:port=1234")
            self.assertRaises(Exception, transport.check_endpoint, ep, listen=True)

        def test_istream_server(self):
            ep = serverFromString(reactor, "tcp:port=1234")
            self.assertTrue(transport.check_endpoint(ep, listen=True))

        def test_istream_server_but_connect(self):
            ep = serverFromString(reactor, "tcp:port=1234")
            self.assertRaises(Exception, transport.check_endpoint, ep)
