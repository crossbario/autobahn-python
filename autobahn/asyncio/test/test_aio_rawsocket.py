import os
from unittest.mock import Mock, call

import pytest

from autobahn.asyncio.rawsocket import (
    PrefixProtocol,
    RawSocketClientProtocol,
    RawSocketServerProtocol,
    WampRawSocketClientFactory,
    WampRawSocketServerFactory,
)
from autobahn.asyncio.util import get_serializers
from autobahn.wamp import message
from autobahn.wamp.types import TransportDetails


@pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)
def test_sers():
    serializers = get_serializers()
    assert len(serializers) > 0
    m = serializers[0]().serialize(message.Abort("close"))
    assert m


@pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)
def test_prefix():
    p = PrefixProtocol()
    transport = Mock()
    receiver = Mock()
    p.stringReceived = receiver
    p.connection_made(transport)
    small_msg = b"\x00\x00\x00\x04abcd"
    p.data_received(small_msg)
    receiver.assert_called_once_with(b"abcd")
    assert len(p._buffer) == 0

    p.sendString(b"abcd")

    # print(transport.write.call_args_list)
    transport.write.assert_has_calls([call(b"\x00\x00\x00\x04"), call(b"abcd")])

    transport.reset_mock()
    receiver.reset_mock()

    big_msg = b"\x00\x00\x00\x0c" + b"0123456789AB"

    p.data_received(big_msg[0:2])
    assert not receiver.called

    p.data_received(big_msg[2:6])
    assert not receiver.called

    p.data_received(big_msg[6:11])
    assert not receiver.called

    p.data_received(big_msg[11:16])
    receiver.assert_called_once_with(b"0123456789AB")

    transport.reset_mock()
    receiver.reset_mock()

    two_messages = (
        b"\x00\x00\x00\x04" + b"abcd" + b"\x00\x00\x00\x05" + b"12345" + b"\x00"
    )
    p.data_received(two_messages)
    receiver.assert_has_calls([call(b"abcd"), call(b"12345")])
    assert p._buffer == b"\x00"


@pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)
def test_is_closed():
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
    assert client.is_closed.done()
    client.connection_made(transport)
    assert not client.is_closed.done()
    client.connection_lost(None)

    assert client.is_closed.done()


@pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)
def test_raw_socket_server1():
    server = RawSocketServerProtocol()
    ser = Mock(return_value=True)
    on_hs = Mock()
    transport = Mock()
    receiver = Mock()
    server.supports_serializer = ser
    server.stringReceived = receiver
    server._on_handshake_complete = on_hs
    server.stringReceived = receiver

    server.connection_made(transport)
    hs = b"\x7f\xf1\x00\x00" + b"\x00\x00\x00\x04abcd"
    server.data_received(hs)

    ser.assert_called_once_with(1)
    on_hs.assert_called_once_with()
    assert transport.write.called
    transport.write.assert_called_once_with(b"\x7f\xf1\x00\x00")
    assert not transport.close.called
    receiver.assert_called_once_with(b"abcd")


@pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)
def test_raw_socket_server_errors():
    server = RawSocketServerProtocol()
    ser = Mock(return_value=True)
    on_hs = Mock()
    transport = Mock()
    receiver = Mock()
    server.supports_serializer = ser
    server.stringReceived = receiver
    server._on_handshake_complete = on_hs
    server.stringReceived = receiver
    server.connection_made(transport)
    server.data_received(b"abcdef")
    transport.close.assert_called_once_with()

    server = RawSocketServerProtocol()
    ser = Mock(return_value=False)
    on_hs = Mock()
    transport = Mock(spec_set=("close", "write", "get_extra_info"))
    receiver = Mock()
    server.supports_serializer = ser
    server.stringReceived = receiver
    server._on_handshake_complete = on_hs
    server.stringReceived = receiver
    server.connection_made(transport)
    server.data_received(b"\x7f\xf1\x00\x00")
    transport.close.assert_called_once_with()
    transport.write.assert_called_once_with(b"\x7f\x10\x00\x00")


@pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)
def test_raw_socket_client1():
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
    client.data_received(b"\x7f\xf1\x00\x00" + b"\x00\x00\x00\x04abcd")
    on_hs.assert_called_once_with()
    assert transport.write.called
    transport.write.called_one_with(b"\x7f\xf1\x00\x00")
    assert not transport.close.called
    receiver.assert_called_once_with(b"abcd")


@pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)
def test_raw_socket_client_error():
    class CP(RawSocketClientProtocol):
        @property
        def serializer_id(self):
            return 1

    client = CP()

    on_hs = Mock()
    transport = Mock(spec_set=("close", "write", "get_extra_info"))
    receiver = Mock()
    client.stringReceived = receiver
    client._on_handshake_complete = on_hs
    client.connection_made(transport)

    client.data_received(b"\x7f\xf1\x00\x01")
    transport.close.assert_called_once_with()


@pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)
def test_wamp_server():
    transport = Mock(spec_set=("abort", "close", "write", "get_extra_info"))
    transport.write = Mock(side_effect=lambda m: messages.append(m))
    server = Mock(spec=["onOpen", "onMessage"])

    def fact_server():
        return server

    messages = []

    proto = WampRawSocketServerFactory(fact_server)()
    proto.connection_made(transport)
    assert proto.transport_details.is_server is True
    assert (
        proto.transport_details.channel_framing
        == TransportDetails.CHANNEL_FRAMING_RAWSOCKET
    )
    assert proto.factory._serializers
    s = proto.factory._serializers[1].RAWSOCKET_SERIALIZER_ID
    proto.data_received(bytes(bytearray([0x7F, 0xF0 | s, 0, 0])))
    assert proto._serializer
    server.onOpen.assert_called_once_with(proto)

    proto.send(message.Abort("close"))
    for d in messages[1:]:
        proto.data_received(d)
    assert server.onMessage.called
    assert isinstance(server.onMessage.call_args[0][0], message.Abort)


@pytest.mark.skipif(
    not os.environ.get("USE_ASYNCIO", False), reason="test runs on asyncio only"
)
def test_wamp_client():
    transport = Mock(spec_set=("abort", "close", "write", "get_extra_info"))
    transport.write = Mock(side_effect=lambda m: messages.append(m))
    client = Mock(spec=["onOpen", "onMessage"])

    def fact_client():
        return client

    messages = []

    proto = WampRawSocketClientFactory(fact_client)()
    proto.connection_made(transport)
    assert proto.transport_details.is_server is False
    assert (
        proto.transport_details.channel_framing
        == TransportDetails.CHANNEL_FRAMING_RAWSOCKET
    )
    assert proto._serializer
    s = proto._serializer.RAWSOCKET_SERIALIZER_ID
    proto.data_received(bytes(bytearray([0x7F, 0xF0 | s, 0, 0])))
    client.onOpen.assert_called_once_with(proto)

    proto.send(message.Abort("close"))
    for d in messages[1:]:
        proto.data_received(d)
    assert client.onMessage.called
    assert isinstance(client.onMessage.call_args[0][0], message.Abort)
