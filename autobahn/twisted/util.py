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
import hashlib
import threading
from typing import Optional, Union, Dict, Any

from twisted.internet.defer import Deferred
from twisted.internet.address import IPv4Address, UNIXAddress
from twisted.internet.interfaces import ITransport, IProcessTransport

from autobahn.wamp.types import TransportDetails

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

try:
    from twisted.internet.interfaces import ISSLTransport
    from twisted.protocols.tls import TLSMemoryBIOProtocol
    from OpenSSL.SSL import Connection
    _HAS_TLS = True
except ImportError:
    _HAS_TLS = False

__all = (
    'sleep',
    'peer2str',
    'transport_channel_id',
    'extract_peer_certificate',
    'create_transport_details',
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


def peer2str(transport: Union[ITransport, IProcessTransport]) -> str:
    """
    Return a *peer descriptor* given a Twisted transport, for example:

    * ``tcp4:127.0.0.1:52914``: a TCPv4 socket
    * ``unix:/tmp/server.sock``: a Unix domain socket
    * ``process:142092``: a Pipe originating from a spawning (parent) process
    * ``pipe``: a Pipe terminating in a spawned (child) process

    :returns: Returns a string representation of the peer of the Twisted transport.
    """
    # IMPORTANT: we need to _first_ test for IProcessTransport
    if IProcessTransport.providedBy(transport):
        # note the PID of the forked process in the peer descriptor
        res = "process:{}".format(transport.pid)
    elif ITransport.providedBy(transport):
        addr: Union[IPv4Address, IPv6Address, UNIXAddress, PipeAddress] = transport.getPeer()
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
            # sadly, we don't have a way to get at the PID of the other side of the pipe
            # res = "pipe"
            res = "process:{0}".format(os.getppid())
        else:
            # gracefully fallback if we can't map the peer's address
            res = "unknown"
    else:
        # gracefully fallback if we can't map the peer's transport
        res = "unknown"
    return res


if not _HAS_TLS:
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
                # expected to receive from the client: contents of the message or None if the TLS handshake has
                # not yet completed.
                tls_finished_msg = connection.get_peer_finished()
            else:
                # for clients XOR resumed sessions, the channel ID is based on the TLS Finished message we sent
                # to the router (=server): contents of the message or None if the TLS handshake has not yet completed.
                tls_finished_msg = connection.get_finished()

            if tls_finished_msg is None:
                # this can occur when:
                #   1. we made a successful connection (in a TCP sense) but something failed with
                #      the TLS handshake (e.g. invalid certificate)
                #   2. the TLS handshake has not yet completed
                return b'\x00' * 32
            else:
                m = hashlib.sha256()
                m.update(tls_finished_msg)
                return m.digest()
        else:
            raise NotImplementedError('should not arrive here (unhandled channel_id_type "{}")'.format(channel_id_type))


if not _HAS_TLS:
    def extract_peer_certificate(transport: object) -> Optional[Dict[str, Any]]:
        """
        Dummy when no TLS is available.

        :param transport: Ignored.
        :return: Always return ``None``.
        """
        return None
else:
    def extract_peer_certificate(transport: TLSMemoryBIOProtocol) -> Optional[Dict[str, Any]]:
        """
        Extract TLS x509 client certificate information from a Twisted stream transport, and
        return a dict with x509 TLS client certificate information (if the client provided a
        TLS client certificate).

        :param transport: The secure transport from which to extract the peer certificate (if present).
        :returns: If the peer provided a certificate, the parsed certificate information set.
        """
        # check if the Twisted transport is a TLSMemoryBIOProtocol
        if not (ISSLTransport.providedBy(transport) and hasattr(transport, 'getPeerCertificate')):
            return None

        cert = transport.getPeerCertificate()
        if cert:
            # extract x509 name components from an OpenSSL X509Name object
            def maybe_bytes(_value):
                if isinstance(_value, bytes):
                    return _value.decode('utf8')
                else:
                    return _value

            result = {
                'md5': '{}'.format(maybe_bytes(cert.digest('md5'))).upper(),
                'sha1': '{}'.format(maybe_bytes(cert.digest('sha1'))).upper(),
                'sha256': '{}'.format(maybe_bytes(cert.digest('sha256'))).upper(),
                'expired': bool(cert.has_expired()),
                'hash': maybe_bytes(cert.subject_name_hash()),
                'serial': int(cert.get_serial_number()),
                'signature_algorithm': maybe_bytes(cert.get_signature_algorithm()),
                'version': int(cert.get_version()),
                'not_before': maybe_bytes(cert.get_notBefore()),
                'not_after': maybe_bytes(cert.get_notAfter()),
                'extensions': []
            }

            for i in range(cert.get_extension_count()):
                ext = cert.get_extension(i)
                ext_info = {
                    'name': '{}'.format(maybe_bytes(ext.get_short_name())),
                    'value': '{}'.format(maybe_bytes(ext)),
                    'critical': ext.get_critical() != 0
                }
                result['extensions'].append(ext_info)

            for entity, name in [('subject', cert.get_subject()), ('issuer', cert.get_issuer())]:
                result[entity] = {}
                for key, value in name.get_components():
                    key = maybe_bytes(key)
                    value = maybe_bytes(value)
                    result[entity]['{}'.format(key).lower()] = '{}'.format(value)

            return result


def create_transport_details(transport: Union[ITransport, IProcessTransport], is_server: bool) -> TransportDetails:
    """
    Create transport details from Twisted transport.

    :param transport: The Twisted transport to extract information from.
    :param is_server: Flag indicating whether this transport side is a "server" (as in TCP server).
    :return: Transport details object filled with information from the Twisted transport.
    """
    peer = peer2str(transport)

    own_pid = os.getpid()
    if hasattr(threading, 'get_native_id'):
        # New in Python 3.8
        # https://docs.python.org/3/library/threading.html?highlight=get_native_id#threading.get_native_id
        own_tid = threading.get_native_id()
    else:
        own_tid = threading.get_ident()
    own_fd = -1

    if _HAS_TLS and ISSLTransport.providedBy(transport):
        channel_id = {
            # this will only be filled when the TLS opening handshake is complete (!)
            'tls-unique': transport_channel_id(transport, is_server, 'tls-unique'),
        }
        channel_type = TransportDetails.CHANNEL_TYPE_TLS
        peer_cert = extract_peer_certificate(transport)
        is_secure = True
    else:
        channel_id = {}
        channel_type = TransportDetails.CHANNEL_TYPE_TCP
        peer_cert = None
        is_secure = False

    # FIXME: really set a default (websocket)?
    channel_framing = TransportDetails.CHANNEL_FRAMING_WEBSOCKET

    td = TransportDetails(channel_type=channel_type, channel_framing=channel_framing, peer=peer,
                          is_server=is_server, own_pid=own_pid, own_tid=own_tid, own_fd=own_fd,
                          is_secure=is_secure, channel_id=channel_id, peer_cert=peer_cert)

    return td
