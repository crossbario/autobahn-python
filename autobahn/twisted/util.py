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
from typing import Optional, Union

from twisted.internet.defer import Deferred
from twisted.internet.address import IPv4Address, UNIXAddress
try:
    from twisted.internet.stdio import PipeAddress
except ImportError:
    # stdio.PipeAddress is only avail on Twisted 13.0+
    PipeAddress = type(None)

try:
    from twisted.internet.address import IPv6Address
    _HAS_IPV6 = True
except ImportError:
    _HAS_IPV6 = False
    IPv6Address = type(None)

__all = (
    'sleep',
    'peer2str',
    'transport_channel_id'
)


def sleep(delay, reactor=None):
    """
    Inline sleep for use in co-routines (Twisted ``inlineCallback`` decorated functions).

    .. seealso::
       * `twisted.internet.defer.inlineCallbacks <http://twistedmatrix.com/documents/current/api/twisted.internet.defer.html#inlineCallbacks>`__
       * `twisted.internet.interfaces.IReactorTime <http://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IReactorTime.html>`__

    :param delay: Time to sleep in seconds.
    :type delay: float
    :param reactor: The Twisted reactor to use.
    :type reactor: None or provider of ``IReactorTime``.
    """
    if not reactor:
        from twisted.internet import reactor
    d = Deferred()
    reactor.callLater(delay, d.callback, None)
    return d


def peer2str(addr: Union[IPv4Address, IPv6Address, UNIXAddress, PipeAddress]) -> str:
    """
    Convert a Twisted address as returned from ``self.transport.getPeer()`` to a string.

    :returns: Returns a string representation of the peer on a Twisted transport.
    """
    if isinstance(addr, IPv4Address):
        res = "tcp4:{0}:{1}".format(addr.host, addr.port)
    elif _HAS_IPV6 and isinstance(addr, IPv6Address):
        res = "tcp6:{0}:{1}".format(addr.host, addr.port)
    elif isinstance(addr, UNIXAddress):
        if addr.name:
            res = "unix:{0}".format(addr.name)
        else:
            res = "unix"
    elif isinstance(addr, PipeAddress):
        res = "<pipe>"
    else:
        # gracefully fallback if we can't map the peer's address
        res = "?:{0}".format(addr)

    return res


try:
    from twisted.protocols.tls import TLSMemoryBIOProtocol
    from OpenSSL.SSL import Connection
except ImportError:
    def transport_channel_id(transport: object, is_server: bool, channel_id_type: Optional[str] = None) -> Optional[bytes]:
        if channel_id_type is None:
            return b'\x00' * 32
        else:
            raise RuntimeError('cannot determine TLS channel ID of type "{}" when TLS is not available on this system'.format(channel_id_type))
else:
    def transport_channel_id(transport: object, is_server: bool, channel_id_type: Optional[str] = None) -> Optional[bytes]:
        """
        Return TLS channel ID of WAMP transport of the given TLS channel ID type.

        Application-layer user authentication protocols are vulnerable to generic credential forwarding attacks,
        where an authentication credential sent by a client C to a server M may then be used by M to impersonate C at
        another server S.
        To prevent such credential forwarding attacks, modern authentication protocols rely on channel bindings.
        For example, WAMP-cryptosign can use the tls-unique channel identifier provided by the TLS layer to strongly
        bind authentication credentials to the underlying channel, so that a credential received on one TLS channel
        cannot be forwarded on another.

        :param transport: The Twisted TLS transport to extract the TLS channel ID from. If the transport isn't
            TLS based, and non-empty ``channel_id_type`` is requested, ``None`` will be returned. If the transport
            is indeed TLS based, an empty ``channel_id_type`` of ``None`` is requested, 32 NUL bytes will be returned.
        :param is_server: Flag indicating that the transport is a server transport.
        :param channel_id_type: TLS channel ID type, if set currently only ``"tls-unique"`` is supported.
        :returns: The TLS channel ID (32 bytes).
        """
        if channel_id_type is None:
            return b'\x00' * 32

        if channel_id_type not in ['tls-unique']:
            raise RuntimeError('invalid TLS channel ID type "{}" requested'.format(channel_id_type))

        if not isinstance(transport, TLSMemoryBIOProtocol):
            raise RuntimeError(
                'cannot determine TLS channel ID of type "{}" when TLS is not available on this transport {}'.format(
                    channel_id_type, type(transport)))

        # get access to the OpenSSL connection underlying the Twisted protocol
        # https://twistedmatrix.com/documents/current/api/twisted.protocols.tls.TLSMemoryBIOProtocol.html#getHandle
        connection: Connection = transport.getHandle()
        assert connection and isinstance(connection, Connection)

        # Obtain latest TLS Finished message that we expected from peer, or None if handshake is not completed.
        # http://www.pyopenssl.org/en/stable/api/ssl.html#OpenSSL.SSL.Connection.get_peer_finished
        is_not_resumed = True

        if channel_id_type == 'tls-unique':
            # see also: https://bugs.python.org/file22646/tls_channel_binding.patch
            if is_server != is_not_resumed:
                # for routers (=servers) XOR new sessions, the channel ID is based on the TLS Finished message we
                # expected to receive from the client
                tls_finished_msg = connection.get_peer_finished()
            else:
                # for clients XOR resumed sessions, the channel ID is based on the TLS Finished message we sent
                # to the router (=server)
                tls_finished_msg = connection.get_finished()

            if tls_finished_msg is None:
                # this can occur if we made a successful connection (in a
                # TCP sense) but something failed with the TLS handshake
                # (e.g. invalid certificate)
                return b'\x00' * 32
            else:
                m = hashlib.sha256()
                m.update(tls_finished_msg)
                return m.digest()
        else:
            raise NotImplementedError('should not arrive here (unhandled channel_id_type "{}")'.format(channel_id_type))
