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


def peer2str(addr):
    """
    Convert a Twisted address as returned from ``self.transport.getPeer()`` to a string.

    :returns: Returns a string representation of the peer on a Twisted transport.
    :rtype: unicode
    """
    if isinstance(addr, IPv4Address):
        res = "tcp4:{0}:{1}".format(addr.host, addr.port)
    elif _HAS_IPV6 and isinstance(addr, IPv6Address):
        res = "tcp6:{0}:{1}".format(addr.host, addr.port)
    elif isinstance(addr, UNIXAddress):
        res = "unix:{0}".format(addr.name)
    elif isinstance(addr, PipeAddress):
        res = "<pipe>"
    else:
        # gracefully fallback if we can't map the peer's address
        res = "?:{0}".format(addr)

    return res


try:
    from twisted.protocols.tls import TLSMemoryBIOProtocol
except ImportError:
    def transport_channel_id(transport: object, is_server: bool, channel_id_type: Optional[str] = None) -> bytes:
        if channel_id_type is None:
            return b'\x00' * 32
else:
    def transport_channel_id(transport: TLSMemoryBIOProtocol, is_server: bool, channel_id_type: Optional[str] = None) -> bytes:
        """
        Application-layer user authentication protocols are vulnerable to generic
        credential forwarding attacks, where an authentication credential sent by
        a client C to a server M may then be used by M to impersonate C at another
        server S. To prevent such credential forwarding attacks, modern authentication
        protocols rely on channel bindings. For example, WAMP-cryptosign can use
        the tls-unique channel identifier provided by the TLS layer to strongly bind
        authentication credentials to the underlying channel, so that a credential
        received on one TLS channel cannot be forwarded on another.

        :param transport: The Twisted TLS transport to extract the TLS channel ID from.
        :param is_server: Flag indicating the transport is for a server.
        :param channel_id_type: TLS channel ID type, currently only "tls-unique" is supported.
        :returns: The TLS channel id (32 bytes).
        """
        if channel_id_type is None:
            return b'\x00' * 32

        if channel_id_type not in ['tls-unique']:
            raise Exception("invalid channel ID type {}".format(channel_id_type))

        # transport:                instance of :class:`twisted.protocols.tls.TLSMemoryBIOProtocol`
        # transport._tlsConnection: instance of :class:`OpenSSL.SSL.Connection`
        if not hasattr(transport, '_tlsConnection'):
            print("TLS transport channel_id for tls-unique requested, but _tlsConnection not found on transport {}".format(dir(transport)))
            return b'\x00' * 32

        # Obtain latest TLS Finished message that we expected from peer, or None if handshake is not completed.
        # http://www.pyopenssl.org/en/stable/api/ssl.html#OpenSSL.SSL.Connection.get_peer_finished
        is_not_resumed = True

        if channel_id_type == 'tls-unique':
            # see also: https://bugs.python.org/file22646/tls_channel_binding.patch
            if is_server != is_not_resumed:
                # for routers (=servers) XOR new sessions, the channel ID is based on the TLS Finished message we
                # expected to receive from the client
                tls_finished_msg = transport._tlsConnection.get_peer_finished()
            else:
                # for clients XOR resumed sessions, the channel ID is based on the TLS Finished message we sent
                # to the router (=server)
                tls_finished_msg = transport._tlsConnection.get_finished()

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
            assert False, 'should not arrive here'
