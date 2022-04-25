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

from unittest.mock import Mock

import txaio
txaio.use_twisted()

from autobahn.util import wildcards2patterns
from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketClientProtocol
from autobahn.wamp.types import TransportDetails
from autobahn.websocket.types import ConnectingRequest
from twisted.python.failure import Failure
from twisted.internet.error import ConnectionDone, ConnectionAborted, \
    ConnectionLost
from twisted.trial import unittest
try:
    from twisted.internet.testing import StringTransport
except ImportError:
    from twisted.test.proto_helpers import StringTransport
from autobahn.testutil import FakeTransport


class ExceptionHandlingTests(unittest.TestCase):
    """
    Tests that we format various exception variations properly during
    connectionLost
    """

    def setUp(self):
        self.factory = WebSocketServerFactory()
        self.proto = WebSocketServerProtocol()
        self.proto.factory = self.factory
        self.proto.log = Mock()

    def tearDown(self):
        for call in [
                self.proto.autoPingPendingCall,
                self.proto.autoPingTimeoutCall,
                self.proto.openHandshakeTimeoutCall,
                self.proto.closeHandshakeTimeoutCall,
        ]:
            if call is not None:
                call.cancel()

    def test_connection_done(self):
        # pretend we connected
        self.proto._connectionMade()

        self.proto.connectionLost(Failure(ConnectionDone()))

        messages = ' '.join([str(x[1]) for x in self.proto.log.mock_calls])
        self.assertTrue('closed cleanly' in messages)

    def test_connection_aborted(self):
        # pretend we connected
        self.proto._connectionMade()

        self.proto.connectionLost(Failure(ConnectionAborted()))

        messages = ' '.join([str(x[1]) for x in self.proto.log.mock_calls])
        self.assertTrue(' aborted ' in messages)

    def test_connection_lost(self):
        # pretend we connected
        self.proto._connectionMade()

        self.proto.connectionLost(Failure(ConnectionLost()))

        messages = ' '.join([str(x[1]) for x in self.proto.log.mock_calls])
        self.assertTrue(' was lost ' in messages)

    def test_connection_lost_arg(self):
        # pretend we connected
        self.proto._connectionMade()

        self.proto.connectionLost(Failure(ConnectionLost("greetings")))

        messages = ' '.join([str(x[1]) + str(x[2]) for x in self.proto.log.mock_calls])
        self.assertTrue(' was lost ' in messages)
        self.assertTrue('greetings' in messages)


class Hixie76RejectionTests(unittest.TestCase):
    """
    Hixie-76 should not be accepted by an Autobahn server.
    """
    def test_handshake_fails(self):
        """
        A handshake from a client only supporting Hixie-76 will fail.
        """
        t = FakeTransport()
        f = WebSocketServerFactory()
        p = WebSocketServerProtocol()
        p.factory = f
        p.transport = t

        # from http://tools.ietf.org/html/draft-hixie-thewebsocketprotocol-76
        http_request = b"GET /demo HTTP/1.1\r\nHost: example.com\r\nConnection: Upgrade\r\nSec-WebSocket-Key2: 12998 5 Y3 1  .P00\r\nSec-WebSocket-Protocol: sample\r\nUpgrade: WebSocket\r\nSec-WebSocket-Key1: 4 @1  46546xW%0l 1 5\r\nOrigin: http://example.com\r\n\r\n^n:ds[4U"

        p.openHandshakeTimeout = 0
        p._connectionMade()
        p.data = http_request
        p.processHandshake()
        self.assertIn(b"HTTP/1.1 400", t._written)
        self.assertIn(b"Hixie76 protocol not supported", t._written)


class WebSocketOriginMatching(unittest.TestCase):
    """
    Test that we match Origin: headers properly, when asked to
    """

    def setUp(self):
        self.factory = WebSocketServerFactory()
        self.factory.setProtocolOptions(
            allowedOrigins=['127.0.0.1:*', '*.example.com:*']
        )
        self.proto = WebSocketServerProtocol()
        self.proto.transport = StringTransport()
        self.proto.factory = self.factory
        self.proto.failHandshake = Mock()
        self.proto._connectionMade()

    def tearDown(self):
        for call in [
                self.proto.autoPingPendingCall,
                self.proto.autoPingTimeoutCall,
                self.proto.openHandshakeTimeoutCall,
                self.proto.closeHandshakeTimeoutCall,
        ]:
            if call is not None:
                call.cancel()

    def test_match_full_origin(self):
        self.proto.data = b"\r\n".join([
            b'GET /ws HTTP/1.1',
            b'Host: www.example.com',
            b'Sec-WebSocket-Version: 13',
            b'Origin: http://www.example.com.malicious.com',
            b'Sec-WebSocket-Extensions: permessage-deflate',
            b'Sec-WebSocket-Key: tXAxWFUqnhi86Ajj7dRY5g==',
            b'Connection: keep-alive, Upgrade',
            b'Upgrade: websocket',
            b'\r\n',  # last string doesn't get a \r\n from join()
        ])
        self.proto.consumeData()

        self.assertTrue(self.proto.failHandshake.called, "Handshake should have failed")
        arg = self.proto.failHandshake.mock_calls[0][1][0]
        self.assertTrue('not allowed' in arg)

    def test_match_wrong_scheme_origin(self):
        # some monkey-business since we already did this in setUp, but
        # we want a different set of matching origins
        self.factory.setProtocolOptions(
            allowedOrigins=['http://*.example.com:*']
        )
        self.proto.allowedOriginsPatterns = self.factory.allowedOriginsPatterns
        self.proto.allowedOrigins = self.factory.allowedOrigins

        # the actual test
        self.factory.isSecure = False
        self.proto.data = b"\r\n".join([
            b'GET /ws HTTP/1.1',
            b'Host: www.example.com',
            b'Sec-WebSocket-Version: 13',
            b'Origin: https://www.example.com',
            b'Sec-WebSocket-Extensions: permessage-deflate',
            b'Sec-WebSocket-Key: tXAxWFUqnhi86Ajj7dRY5g==',
            b'Connection: keep-alive, Upgrade',
            b'Upgrade: websocket',
            b'\r\n',  # last string doesn't get a \r\n from join()
        ])
        self.proto.consumeData()

        self.assertTrue(self.proto.failHandshake.called, "Handshake should have failed")
        arg = self.proto.failHandshake.mock_calls[0][1][0]
        self.assertTrue('not allowed' in arg)

    def test_match_origin_secure_scheme(self):
        self.factory.isSecure = True
        self.factory.port = 443
        self.proto.data = b"\r\n".join([
            b'GET /ws HTTP/1.1',
            b'Host: www.example.com',
            b'Sec-WebSocket-Version: 13',
            b'Origin: https://www.example.com',
            b'Sec-WebSocket-Extensions: permessage-deflate',
            b'Sec-WebSocket-Key: tXAxWFUqnhi86Ajj7dRY5g==',
            b'Connection: keep-alive, Upgrade',
            b'Upgrade: websocket',
            b'\r\n',  # last string doesn't get a \r\n from join()
        ])
        self.proto.consumeData()

        self.assertFalse(self.proto.failHandshake.called, "Handshake should have succeeded")

    def test_match_origin_documentation_example(self):
        """
        Test the examples from the docs
        """
        self.factory.setProtocolOptions(
            allowedOrigins=['*://*.example.com:*']
        )
        self.factory.isSecure = True
        self.factory.port = 443
        self.proto.data = b"\r\n".join([
            b'GET /ws HTTP/1.1',
            b'Host: www.example.com',
            b'Sec-WebSocket-Version: 13',
            b'Origin: http://www.example.com',
            b'Sec-WebSocket-Extensions: permessage-deflate',
            b'Sec-WebSocket-Key: tXAxWFUqnhi86Ajj7dRY5g==',
            b'Connection: keep-alive, Upgrade',
            b'Upgrade: websocket',
            b'\r\n',  # last string doesn't get a \r\n from join()
        ])
        self.proto.consumeData()

        self.assertFalse(self.proto.failHandshake.called, "Handshake should have succeeded")

    def test_match_origin_examples(self):
        """
        All the example origins from RFC6454 (3.2.1)
        """
        # we're just testing the low-level function here...
        from autobahn.websocket.protocol import _is_same_origin, _url_to_origin
        policy = wildcards2patterns(['*example.com:*'])

        # should parametrize test ...
        for url in ['http://example.com/', 'http://example.com:80/',
                    'http://example.com/path/file',
                    'http://example.com/;semi=true',
                    # 'http://example.com./',
                    '//example.com/',
                    'http://@example.com']:
            self.assertTrue(_is_same_origin(_url_to_origin(url), 'http', 80, policy), url)

    def test_match_origin_counter_examples(self):
        """
        All the example 'not-same' origins from RFC6454 (3.2.1)
        """
        # we're just testing the low-level function here...
        from autobahn.websocket.protocol import _is_same_origin, _url_to_origin
        policy = wildcards2patterns(['example.com'])

        for url in ['http://ietf.org/', 'http://example.org/',
                    'https://example.com/', 'http://example.com:8080/',
                    'http://www.example.com/']:
            self.assertFalse(_is_same_origin(_url_to_origin(url), 'http', 80, policy))

    def test_match_origin_edge(self):
        # we're just testing the low-level function here...
        from autobahn.websocket.protocol import _is_same_origin, _url_to_origin
        policy = wildcards2patterns(['http://*example.com:80'])

        self.assertTrue(
            _is_same_origin(_url_to_origin('http://example.com:80'), 'http', 80, policy)
        )
        self.assertFalse(
            _is_same_origin(_url_to_origin('http://example.com:81'), 'http', 81, policy)
        )
        self.assertFalse(
            _is_same_origin(_url_to_origin('https://example.com:80'), 'http', 80, policy)
        )

    def test_origin_from_url(self):
        from autobahn.websocket.protocol import _url_to_origin

        # basic function
        self.assertEqual(
            _url_to_origin('http://example.com'),
            ('http', 'example.com', 80)
        )
        # should lower-case scheme
        self.assertEqual(
            _url_to_origin('hTTp://example.com'),
            ('http', 'example.com', 80)
        )

    def test_origin_file(self):
        from autobahn.websocket.protocol import _url_to_origin
        self.assertEqual('null', _url_to_origin('file:///etc/passwd'))

    def test_origin_null(self):
        from autobahn.websocket.protocol import _is_same_origin, _url_to_origin
        self.assertEqual('null', _url_to_origin('null'))
        self.assertFalse(
            _is_same_origin(_url_to_origin('null'), 'http', 80, [])
        )
        self.assertFalse(
            _is_same_origin(_url_to_origin('null'), 'https', 80, [])
        )
        self.assertFalse(
            _is_same_origin(_url_to_origin('null'), '', 80, [])
        )
        self.assertFalse(
            _is_same_origin(_url_to_origin('null'), None, 80, [])
        )


class WebSocketXForwardedFor(unittest.TestCase):
    """
    Test that (only) a trusted X-Forwarded-For can replace the peer address.
    """

    def setUp(self):
        self.factory = WebSocketServerFactory()
        self.factory.setProtocolOptions(
            trustXForwardedFor=2
        )
        self.proto = WebSocketServerProtocol()
        self.proto.transport = StringTransport()
        self.proto.factory = self.factory
        self.proto.failHandshake = Mock()
        self.proto._connectionMade()

    def tearDown(self):
        for call in [
                self.proto.autoPingPendingCall,
                self.proto.autoPingTimeoutCall,
                self.proto.openHandshakeTimeoutCall,
                self.proto.closeHandshakeTimeoutCall,
        ]:
            if call is not None:
                call.cancel()

    def test_trusted_addresses(self):
        self.proto.data = b"\r\n".join([
            b'GET /ws HTTP/1.1',
            b'Host: www.example.com',
            b'Origin: http://www.example.com',
            b'Sec-WebSocket-Version: 13',
            b'Sec-WebSocket-Extensions: permessage-deflate',
            b'Sec-WebSocket-Key: tXAxWFUqnhi86Ajj7dRY5g==',
            b'Connection: keep-alive, Upgrade',
            b'Upgrade: websocket',
            b'X-Forwarded-For: 1.2.3.4, 2.3.4.5, 111.222.33.44',
            b'\r\n',  # last string doesn't get a \r\n from join()
        ])
        self.proto.consumeData()

        self.assertEquals(
            self.proto.peer, "2.3.4.5",
            "The second address in X-Forwarded-For should have been picked as the peer address")


class OnConnectingTests(unittest.TestCase):
    """
    Tests related to onConnecting callback

    These tests are testing generic behavior, but are somewhat tied to
    'a framework' so we're just testing using Twisted-specifics here.
    """

    def test_on_connecting_client_fails(self):

        MAGIC_STR = 'bad stuff'

        class TestProto(WebSocketClientProtocol):
            state = None
            wasClean = True
            log = Mock()

            def onConnecting(self, transport_details):
                raise RuntimeError(MAGIC_STR)

        proto = TestProto()
        proto.transport = FakeTransport()
        d = proto.startHandshake()
        self.successResultOf(d)  # error is ignored
        # ... but error should be logged
        self.assertTrue(len(proto.log.mock_calls) > 0)
        magic_found = False
        for i in range(len(proto.log.mock_calls)):
            if MAGIC_STR in str(proto.log.mock_calls[i]):
                magic_found = True
        self.assertTrue(magic_found, 'MAGIC_STR not found when expected')

    def test_on_connecting_client_success(self):

        class TestProto(WebSocketClientProtocol):
            state = None
            wasClean = True
            perMessageCompressionOffers = []
            version = 18
            openHandshakeTimeout = 5
            log = Mock()

            def onConnecting(self, transport_details):
                return ConnectingRequest(
                    host="example.com",
                    port=443,
                    resource="/ws",
                )

        proto = TestProto()
        proto.transport = FakeTransport()
        proto.factory = Mock()
        proto._connectionMade()

        d = proto.startHandshake()
        req = self.successResultOf(d)
        self.assertEqual("example.com", req.host)
        self.assertEqual(443, req.port)
        self.assertEqual("/ws", req.resource)

    def test_str_transport(self):
        details = TransportDetails(
            channel_type=TransportDetails.CHANNEL_TYPE_FUNCTION,
            peer="example.com",
            is_secure=False,
            channel_id={},
        )
        # we can str() this and it doesn't fail
        str(details)

    def test_str_connecting(self):
        req = ConnectingRequest(host="example.com", port="1234", resource="/ws")
        # we can str() this and it doesn't fail
        str(req)
