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

import hashlib
from typing import Optional

try:
    from asyncio import sleep  # noqa
except ImportError:
    # Trollius >= 0.3 was renamed to asyncio
    # noinspection PyUnresolvedReferences
    from trollius import sleep  # noqa

__all = (
    'sleep',
    'peer2str',
    'transport_channel_id',
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

    if channel_id_type not in ['tls-unique']:
        raise Exception("invalid channel ID type {}".format(channel_id_type))

    ssl_obj = transport.get_extra_info('ssl_object')
    if ssl_obj is None:
        raise Exception("TLS transport channel_id for tls-unique requested, but ssl_obj not found on transport")

    if not hasattr(ssl_obj, 'get_channel_binding'):
        raise Exception("TLS transport channel_id for tls-unique requested, but get_channel_binding not found on ssl_obj")

    # https://python.readthedocs.io/en/latest/library/ssl.html#ssl.SSLSocket.get_channel_binding
    # https://tools.ietf.org/html/rfc5929.html
    tls_finished_msg = ssl_obj.get_channel_binding(cb_type='tls-unique')

    m = hashlib.sha256()
    m.update(tls_finished_msg)
    channel_id = m.digest()

    return channel_id


def peer2str(peer):
    if isinstance(peer, tuple):
        ip_ver = 4 if len(peer) == 2 else 6
        return "tcp{2}:{0}:{1}".format(peer[0], peer[1], ip_ver)
    elif isinstance(peer, str):
        return "unix:{0}".format(peer)
    else:
        return "?:{0}".format(peer)


def get_serializers():
    from autobahn.wamp import serializer

    serializers = ['CBORSerializer', 'MsgPackSerializer', 'UBJSONSerializer', 'JsonSerializer']
    serializers = list(filter(lambda x: x, map(lambda s: getattr(serializer, s) if hasattr(serializer, s)
                                               else None, serializers)))
    return serializers
