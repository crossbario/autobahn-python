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

import hashlib
from subprocess import Popen
from typing import Optional
import asyncio
from asyncio import sleep  # noqa

from autobahn.wamp.types import TransportDetails

__all = (
    'sleep',
    'peer2str',
    'transport_channel_id',
    'create_transport_details',
)


def transport_channel_id(transport, is_server: bool, channel_id_type: Optional[str] = None) -> bytes:
    """
    Application-layer user authentication protocols are vulnerable to generic
    credential forwarding attacks, where an authentication credential sent by
    a client C to a server M may then be used by M to impersonate C at another
    server S. To prevent such credential forwarding attacks, modern authentication
    protocols rely on channel bindings. For example, WAMP-cryptosign can use
    the tls-unique channel identifier provided by the TLS layer to strongly bind
    authentication credentials to the underlying channel, so that a credential
    received on one TLS channel cannot be forwarded on another.

    :param transport: The asyncio TLS transport to extract the TLS channel ID from.
    :param is_server: Flag indicating the transport is for a server.
    :param channel_id_type: TLS channel ID type, currently only "tls-unique" is supported.
    :returns: The TLS channel id (32 bytes).
    """
    if channel_id_type is None:
        return b'\x00' * 32

    # ssl.CHANNEL_BINDING_TYPES
    if channel_id_type not in ['tls-unique']:
        raise Exception("invalid channel ID type {}".format(channel_id_type))

    ssl_obj = transport.get_extra_info('ssl_object')
    if ssl_obj is None:
        raise Exception("TLS transport channel_id for tls-unique requested, but ssl_obj not found on transport")

    if not hasattr(ssl_obj, 'get_channel_binding'):
        raise Exception("TLS transport channel_id for tls-unique requested, but get_channel_binding not found on ssl_obj")

    # https://python.readthedocs.io/en/latest/library/ssl.html#ssl.SSLSocket.get_channel_binding
    # https://tools.ietf.org/html/rfc5929.html
    tls_finished_msg: bytes = ssl_obj.get_channel_binding(cb_type='tls-unique')

    if type(tls_finished_msg) != bytes:
        return b'\x00' * 32
    else:
        m = hashlib.sha256()
        m.update(tls_finished_msg)
        channel_id = m.digest()
        return channel_id


def peer2str(transport: asyncio.transports.BaseTransport) -> str:
    # https://docs.python.org/3.9/library/asyncio-protocol.html?highlight=get_extra_info#asyncio.BaseTransport.get_extra_info
    # https://docs.python.org/3.9/library/socket.html#socket.socket.getpeername
    try:
        peer = transport.get_extra_info('peername')
        if isinstance(peer, tuple):
            ip_ver = 4 if len(peer) == 2 else 6
            return "tcp{2}:{0}:{1}".format(peer[0], peer[1], ip_ver)
        elif isinstance(peer, str):
            return "unix:{0}".format(peer)
        else:
            return "?:{0}".format(peer)
    except:
        pass

    try:
        proc: Popen = transport.get_extra_info('subprocess')
        # return 'process:{}'.format(transport.pid)
        return 'process:{}'.format(proc.pid)
    except:
        pass

    try:
        pipe = transport.get_extra_info('pipe')
        return 'pipe:{}'.format(pipe)
    except:
        pass

    # gracefully fallback if we can't map the peer's transport
    return 'unknown'


def get_serializers():
    from autobahn.wamp import serializer

    serializers = ['CBORSerializer', 'MsgPackSerializer', 'UBJSONSerializer', 'JsonSerializer']
    serializers = list(filter(lambda x: x, map(lambda s: getattr(serializer, s) if hasattr(serializer, s)
                                               else None, serializers)))
    return serializers


def create_transport_details(transport, is_server: bool) -> TransportDetails:
    # Internal helper. Base class calls this to create a TransportDetails
    peer = peer2str(transport)

    # https://docs.python.org/3.9/library/asyncio-protocol.html?highlight=get_extra_info#asyncio.BaseTransport.get_extra_info
    is_secure = transport.get_extra_info('peercert', None) is not None
    if is_secure:
        channel_id = {
            'tls-unique': transport_channel_id(transport, is_server, 'tls-unique'),
        }
        channel_type = TransportDetails.CHANNEL_TYPE_TLS
        peer_cert = None
    else:
        channel_id = {}
        channel_type = TransportDetails.CHANNEL_TYPE_TCP
        peer_cert = None
    channel_framing = TransportDetails.CHANNEL_FRAMING_WEBSOCKET

    return TransportDetails(channel_type=channel_type, channel_framing=channel_framing,
                            peer=peer, is_server=is_server, is_secure=is_secure,
                            channel_id=channel_id, peer_cert=peer_cert)
