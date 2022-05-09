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

import os
from unittest.mock import Mock, patch

if os.environ.get('USE_TWISTED', False):
    from autobahn.twisted.component import Component
    from zope.interface import directlyProvides
    from autobahn.wamp.message import Welcome, Goodbye, Hello, Abort
    from autobahn.wamp.serializer import JsonSerializer
    from autobahn.testutil import FakeTransport
    from twisted.internet.interfaces import IStreamClientEndpoint
    from twisted.internet.defer import inlineCallbacks, succeed, Deferred
    from twisted.internet.task import Clock
    from twisted.trial import unittest
    from txaio.testutil import replace_loop

    class ConnectionTests(unittest.TestCase):

        def setUp(self):
            pass

        @patch('txaio.sleep', return_value=succeed(None))
        @inlineCallbacks
        def test_successful_connect(self, fake_sleep):
            endpoint = Mock()
            joins = []

            def joined(session, details):
                joins.append((session, details))
                return session.leave()
            directlyProvides(endpoint, IStreamClientEndpoint)
            component = Component(
                transports={
                    "type": "websocket",
                    "url": "ws://127.0.0.1/ws",
                    "endpoint": endpoint,
                }
            )
            component.on('join', joined)

            def connect(factory, **kw):
                proto = factory.buildProtocol('ws://localhost/')
                transport = FakeTransport()
                proto.makeConnection(transport)

                from autobahn.websocket.protocol import WebSocketProtocol
                from base64 import b64encode
                from hashlib import sha1
                key = proto.websocket_key + WebSocketProtocol._WS_MAGIC
                proto.data = (
                    b"HTTP/1.1 101 Switching Protocols\x0d\x0a"
                    b"Upgrade: websocket\x0d\x0a"
                    b"Connection: upgrade\x0d\x0a"
                    b"Sec-Websocket-Protocol: wamp.2.json\x0d\x0a"
                    b"Sec-Websocket-Accept: " + b64encode(sha1(key).digest()) + b"\x0d\x0a\x0d\x0a"
                )
                proto.processHandshake()

                from autobahn.wamp import role
                features = role.RoleBrokerFeatures(
                    publisher_identification=True,
                    pattern_based_subscription=True,
                    session_meta_api=True,
                    subscription_meta_api=True,
                    subscriber_blackwhite_listing=True,
                    publisher_exclusion=True,
                    subscription_revocation=True,
                    payload_transparency=True,
                    payload_encryption_cryptobox=True,
                )

                msg = Welcome(123456, dict(broker=features), realm='realm')
                serializer = JsonSerializer()
                data, is_binary = serializer.serialize(msg)
                proto.onMessage(data, is_binary)

                msg = Goodbye()
                proto.onMessage(*serializer.serialize(msg))
                proto.onClose(True, 100, "some old reason")

                return succeed(proto)
            endpoint.connect = connect

            # XXX it would actually be nicer if we *could* support
            # passing a reactor in here, but the _batched_timer =
            # make_batched_timer() stuff (slash txaio in general)
            # makes this "hard".
            reactor = Clock()
            with replace_loop(reactor):
                yield component.start(reactor=reactor)
                self.assertTrue(len(joins), 1)
                # make sure we fire all our time-outs
                reactor.advance(3600)

        @patch('txaio.sleep', return_value=succeed(None))
        def test_successful_proxy_connect(self, fake_sleep):
            endpoint = Mock()
            directlyProvides(endpoint, IStreamClientEndpoint)
            component = Component(
                transports={
                    "type": "websocket",
                    "url": "ws://127.0.0.1/ws",
                    "endpoint": endpoint,
                    "proxy": {
                        "host": "10.0.0.0",
                        "port": 65000,
                    },
                    "max_retries": 0,
                },
                is_fatal=lambda _: True,
            )

            @component.on_join
            def joined(session, details):
                return session.leave()

            def connect(factory, **kw):
                return succeed(Mock())
            endpoint.connect = connect

            # XXX it would actually be nicer if we *could* support
            # passing a reactor in here, but the _batched_timer =
            # make_batched_timer() stuff (slash txaio in general)
            # makes this "hard".
            reactor = Clock()

            got_proxy_connect = Deferred()

            def _tcp(host, port, factory, **kw):
                self.assertEqual("10.0.0.0", host)
                self.assertEqual(port, 65000)
                got_proxy_connect.callback(None)
                return endpoint.connect(factory._wrappedFactory)
            reactor.connectTCP = _tcp

            with replace_loop(reactor):
                d = component.start(reactor=reactor)

                def done(x):
                    if not got_proxy_connect.called:
                        got_proxy_connect.callback(x)
                # make sure we fire all our time-outs
                d.addCallbacks(done, done)
                reactor.advance(3600)
                return got_proxy_connect

        @patch('txaio.sleep', return_value=succeed(None))
        @inlineCallbacks
        def test_cancel(self, fake_sleep):
            """
            if we start a component but call .stop before it connects, ever,
            it should still exit properly
            """
            endpoint = Mock()
            directlyProvides(endpoint, IStreamClientEndpoint)
            component = Component(
                transports={
                    "type": "websocket",
                    "url": "ws://127.0.0.1/ws",
                    "endpoint": endpoint,
                }
            )

            def connect(factory, **kw):
                return Deferred()
            endpoint.connect = connect

            # XXX it would actually be nicer if we *could* support
            # passing a reactor in here, but the _batched_timer =
            # make_batched_timer() stuff (slash txaio in general)
            # makes this "hard".
            reactor = Clock()
            with replace_loop(reactor):
                d = component.start(reactor=reactor)
                component.stop()
                yield d

        @inlineCallbacks
        def test_cancel_while_waiting(self):
            """
            if we start a component but call .stop before it connects, ever,
            it should still exit properly -- even if we're 'between'
            connection attempts
            """
            endpoint = Mock()
            directlyProvides(endpoint, IStreamClientEndpoint)
            component = Component(
                transports={
                    "type": "websocket",
                    "url": "ws://127.0.0.1/ws",
                    "endpoint": endpoint,
                    "max_retries": 0,
                    "max_retry_delay": 5,
                    "initial_retry_delay": 5,
                },
            )

            # XXX it would actually be nicer if we *could* support
            # passing a reactor in here, but the _batched_timer =
            # make_batched_timer() stuff (slash txaio in general)
            # makes this "hard".
            reactor = Clock()
            with replace_loop(reactor):

                def connect(factory, **kw):
                    d = Deferred()
                    reactor.callLater(10, d.errback(RuntimeError("no connect for yo")))
                    return d
                endpoint.connect = connect

                d0 = component.start(reactor=reactor)
                assert component._delay_f is not None
                assert not component._done_f.called

                d1 = component.stop()
                assert component._done_f is None
                assert d0.called

                yield d1
                yield d0

        @patch('txaio.sleep', return_value=succeed(None))
        @inlineCallbacks
        def test_connect_no_auth_method(self, fake_sleep):
            endpoint = Mock()

            directlyProvides(endpoint, IStreamClientEndpoint)
            component = Component(
                transports={
                    "type": "websocket",
                    "url": "ws://127.0.0.1/ws",
                    "endpoint": endpoint,
                },
                is_fatal=lambda e: True,
            )

            def connect(factory, **kw):
                proto = factory.buildProtocol('boom')
                proto.makeConnection(Mock())

                from autobahn.websocket.protocol import WebSocketProtocol
                from base64 import b64encode
                from hashlib import sha1
                key = proto.websocket_key + WebSocketProtocol._WS_MAGIC
                proto.data = (
                    b"HTTP/1.1 101 Switching Protocols\x0d\x0a"
                    b"Upgrade: websocket\x0d\x0a"
                    b"Connection: upgrade\x0d\x0a"
                    b"Sec-Websocket-Protocol: wamp.2.json\x0d\x0a"
                    b"Sec-Websocket-Accept: " + b64encode(sha1(key).digest()) + b"\x0d\x0a\x0d\x0a"
                )
                proto.processHandshake()

                from autobahn.wamp import role
                subrole = role.RoleSubscriberFeatures()

                msg = Hello("realm", roles=dict(subscriber=subrole), authmethods=["anonymous"])
                serializer = JsonSerializer()
                data, is_binary = serializer.serialize(msg)
                proto.onMessage(data, is_binary)

                msg = Abort(reason="wamp.error.no_auth_method")
                proto.onMessage(*serializer.serialize(msg))
                proto.onClose(False, 100, "wamp.error.no_auth_method")

                return succeed(proto)
            endpoint.connect = connect

            # XXX it would actually be nicer if we *could* support
            # passing a reactor in here, but the _batched_timer =
            # make_batched_timer() stuff (slash txaio in general)
            # makes this "hard".
            reactor = Clock()
            with replace_loop(reactor):
                with self.assertRaises(RuntimeError) as ctx:
                    d = component.start(reactor=reactor)
                    # make sure we fire all our time-outs
                    reactor.advance(3600)
                    yield d
            self.assertIn(
                "Exhausted all transport",
                str(ctx.exception)
            )

    class InvalidTransportConfigs(unittest.TestCase):

        def test_invalid_key(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    transports=dict(
                        foo='bar',  # totally invalid key
                    ),
                )
            self.assertIn("'foo' is not", str(ctx.exception))

        def test_invalid_key_transport_list(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    transports=[
                        dict(type='websocket', url='ws://127.0.0.1/ws'),
                        dict(foo='bar'),  # totally invalid key
                    ]
                )
            self.assertIn("'foo' is not a valid configuration item", str(ctx.exception))

        def test_invalid_serializer_key(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    transports=[
                        {
                            "url": "ws://127.0.0.1/ws",
                            "serializer": ["quux"],
                        }
                    ]
                )
            self.assertIn("only for rawsocket", str(ctx.exception))

        def test_invalid_serializer(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    transports=[
                        {
                            "url": "ws://127.0.0.1/ws",
                            "serializers": ["quux"],
                        }
                    ]
                )
            self.assertIn("Invalid serializer", str(ctx.exception))

        def test_invalid_serializer_type_0(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    transports=[
                        {
                            "url": "ws://127.0.0.1/ws",
                            "serializers": [1, 2],
                        }
                    ]
                )
            self.assertIn("must be a list", str(ctx.exception))

        def test_invalid_serializer_type_1(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    transports=[
                        {
                            "url": "ws://127.0.0.1/ws",
                            "serializers": 1,
                        }
                    ]
                )
            self.assertIn("must be a list", str(ctx.exception))

        def test_invalid_type_key(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    transports=[
                        {
                            "type": "bad",
                        }
                    ]
                )
            self.assertIn("Invalid transport type", str(ctx.exception))

        def test_invalid_type(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    transports=[
                        "foo"
                    ]
                )
            self.assertIn("invalid WebSocket URL", str(ctx.exception))

        def test_no_url(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    transports=[
                        {
                            "type": "websocket",
                        }
                    ]
                )
            self.assertIn("Transport requires 'url'", str(ctx.exception))

        def test_endpoint_bogus_object(self):
            with self.assertRaises(ValueError) as ctx:
                Component(
                    main=lambda r, s: None,
                    transports=[
                        {
                            "type": "websocket",
                            "url": "ws://example.com/ws",
                            "endpoint": ("not", "a", "dict"),
                        }
                    ]
                )
            self.assertIn("'endpoint' configuration must be", str(ctx.exception))

        def test_endpoint_valid(self):
            Component(
                main=lambda r, s: None,
                transports=[
                    {
                        "type": "websocket",
                        "url": "ws://example.com/ws",
                        "endpoint": {
                            "type": "tcp",
                            "host": "1.2.3.4",
                            "port": "4321",
                        }
                    }
                ]
            )
