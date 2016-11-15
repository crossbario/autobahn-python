import pytest
import os

from unittest import TestCase, main
try:
    from unittest.mock import Mock, call
except ImportError:
    from mock import Mock, call
from autobahn.asyncio.rawsocket import PrefixProtocol, RawSocketClientProtocol, RawSocketServerProtocol, \
    WampRawSocketClientFactory, WampRawSocketServerFactory
from autobahn.asyncio.util import get_serializers
from autobahn.wamp import message


@pytest.mark.skipif(os.environ.get('USE_ASYNCIO', False), reason="Only for asyncio")
class Test(TestCase):

    def test_sers(self):
        serializers = get_serializers()
        self.assertTrue(len(serializers) > 0)
        m = serializers[0]().serialize(message.Abort(u'close'))
        print(m)
        self.assertTrue(m)

    def test_prefix(self):
        p = PrefixProtocol()
        transport = Mock()
        receiver = Mock()
        p.stringReceived = receiver
        p.connection_made(transport)
        small_msg = b'\x00\x00\x00\x04abcd'
        p.data_received(small_msg)
        receiver.assert_called_once_with(b'abcd')
        self.assertEqual(len(p._buffer), 0)

        p.sendString(b'abcd')

        # print(transport.write.call_args_list)
        transport.write.assert_has_calls([call(b'\x00\x00\x00\x04'), call(b'abcd')])

        transport.reset_mock()
        receiver.reset_mock()

        big_msg = b'\x00\x00\x00\x0C' + b'0123456789AB'

        p.data_received(big_msg[0:2])
        self.assertFalse(receiver.called)

        p.data_received(big_msg[2:6])
        self.assertFalse(receiver.called)

        p.data_received(big_msg[6:11])
        self.assertFalse(receiver.called)

        p.data_received(big_msg[11:16])
        receiver.assert_called_once_with(b'0123456789AB')

        transport.reset_mock()
        receiver.reset_mock()

        two_messages = b'\x00\x00\x00\x04' + b'abcd' + b'\x00\x00\x00\x05' + b'12345' + b'\x00'
        p.data_received(two_messages)
        receiver.assert_has_calls([call(b'abcd'), call(b'12345')])
        self.assertEqual(p._buffer, b'\x00')

    def test_is_closed(self):
        class CP(RawSocketClientProtocol):
            @property
            def serializer_id(self):
                return 1
        client = CP()

        on_hs = Mock()
        transport = Mock()
        receiver = Mock()
        client.stringReceived = receiver
        client._on_handshake_complete = on_hs
        self.assertTrue(client.is_closed.done())
        client.connection_made(transport)
        self.assertFalse(client.is_closed.done())
        client.connection_lost(None)

        self.assertTrue(client.is_closed.done())

    def test_raw_socket_server1(self):

        server = RawSocketServerProtocol(max_size=10000)
        ser = Mock(return_value=True)
        on_hs = Mock()
        transport = Mock()
        receiver = Mock()
        server.supports_serializer = ser
        server.stringReceived = receiver
        server._on_handshake_complete = on_hs
        server.stringReceived = receiver

        server.connection_made(transport)
        hs = b'\x7F\xF1\x00\x00' + b'\x00\x00\x00\x04abcd'
        server.data_received(hs)

        ser.assert_called_once_with(1)
        on_hs.assert_called_once_with()
        self.assertTrue(transport.write.called)
        transport.write.assert_called_once_with(b'\x7F\x51\x00\x00')
        self.assertFalse(transport.close.called)
        receiver.assert_called_once_with(b'abcd')

    def test_raw_socket_server_errors(self):

        server = RawSocketServerProtocol(max_size=10000)
        ser = Mock(return_value=True)
        on_hs = Mock()
        transport = Mock()
        receiver = Mock()
        server.supports_serializer = ser
        server.stringReceived = receiver
        server._on_handshake_complete = on_hs
        server.stringReceived = receiver
        server.connection_made(transport)
        server.data_received(b'abcdef')
        transport.close.assert_called_once_with()

        server = RawSocketServerProtocol(max_size=10000)
        ser = Mock(return_value=False)
        on_hs = Mock()
        transport = Mock(spec_set=('close', 'write', 'get_extra_info'))
        receiver = Mock()
        server.supports_serializer = ser
        server.stringReceived = receiver
        server._on_handshake_complete = on_hs
        server.stringReceived = receiver
        server.connection_made(transport)
        server.data_received(b'\x7F\xF1\x00\x00')
        transport.close.assert_called_once_with()
        transport.write.assert_called_once_with(b'\x7F\x10\x00\x00')

    def test_raw_socket_client1(self):
        class CP(RawSocketClientProtocol):
            @property
            def serializer_id(self):
                return 1
        client = CP()

        on_hs = Mock()
        transport = Mock()
        receiver = Mock()
        client.stringReceived = receiver
        client._on_handshake_complete = on_hs

        client.connection_made(transport)
        client.data_received(b'\x7F\xF1\x00\x00' + b'\x00\x00\x00\x04abcd')
        on_hs.assert_called_once_with()
        self.assertTrue(transport.write.called)
        transport.write.called_one_with(b'\x7F\xF1\x00\x00')
        self.assertFalse(transport.close.called)
        receiver.assert_called_once_with(b'abcd')

    def test_raw_socket_client_error(self):
        class CP(RawSocketClientProtocol):
            @property
            def serializer_id(self):
                return 1
        client = CP()

        on_hs = Mock()
        transport = Mock(spec_set=('close', 'write', 'get_extra_info'))
        receiver = Mock()
        client.stringReceived = receiver
        client._on_handshake_complete = on_hs
        client.connection_made(transport)

        client.data_received(b'\x7F\xF1\x00\x01')
        transport.close.assert_called_once_with()

    def test_wamp(self):
        transport = Mock(spec_set=('abort', 'close', 'write', 'get_extra_info'))
        transport.write = Mock(side_effect=lambda m: messages.append(m))
        client = Mock(spec=['onOpen', 'onMessage'])

        def fact():
            return client
        messages = []
        proto = WampRawSocketClientFactory(fact)()
        proto.connection_made(transport)
        self.assertTrue(proto._serializer)
        s = proto._serializer.RAWSOCKET_SERIALIZER_ID
        proto.data_received(bytes(bytearray([0x7F, 0xF0 | s, 0, 0])))
        client.onOpen.assert_called_once_with(proto)
        proto.send(message.Abort(u'close'))
        for d in messages[1:]:
            proto.data_received(d)
        self.assertTrue(client.onMessage.called)
        self.assertTrue(isinstance(client.onMessage.call_args[0][0], message.Abort))

        # server
        transport = Mock(spec_set=('abort', 'close', 'write', 'get_extra_info'))
        transport.write = Mock(side_effect=lambda m: messages.append(m))

        client = None
        server = Mock(spec=['onOpen', 'onMessage'])

        def fact_server():
            return server
        messages = []
        proto = WampRawSocketServerFactory(fact_server)()
        proto.connection_made(transport)
        self.assertTrue(proto.factory._serializers)
        s = proto.factory._serializers[1].RAWSOCKET_SERIALIZER_ID
        proto.data_received(bytes(bytearray([0x7F, 0xF0 | s, 0, 0])))
        self.assertTrue(proto._serializer)
        server.onOpen.assert_called_once_with(proto)
        proto.send(message.Abort(u'close'))
        for d in messages[1:]:
            proto.data_received(d)
        self.assertTrue(server.onMessage.called)
        self.assertTrue(isinstance(server.onMessage.call_args[0][0], message.Abort))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_prefix']
    main()
