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

import asyncio
import hashlib
import ssl
import warnings
from asyncio import sleep  # noqa
from subprocess import Popen
from typing import Any, Optional

from autobahn.util import peer_certificate_details, tls_unique
from autobahn.wamp.types import TransportDetails


def get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    """
    The event loop to use from code that may run before any loop exists (#1952).

    In order: the running loop; else the loop set for this thread with
    ``asyncio.set_event_loop()``; else a new loop, which is then set for this thread.

    ``asyncio.get_event_loop()`` used to create that last loop implicitly. Python 3.12
    and 3.13 deprecate this (``DeprecationWarning: There is no current event loop``),
    and Python 3.14 removes it: there it raises ``RuntimeError`` instead. txaio's
    asyncio backend handles it the same way.
    """
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        pass
    try:
        with warnings.catch_warnings():
            # 3.12 / 3.13: the implicit creation below warns; we replace it anyway
            warnings.simplefilter("ignore", DeprecationWarning)
            loop = asyncio.get_event_loop()
    except RuntimeError:
        # 3.14+: no loop set for this thread
        loop = None
    if loop is None or loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


__all = (
    "sleep",
    "get_or_create_event_loop",
    "peer2str",
    "transport_channel_id",
    "create_transport_details",
    "extract_peer_certificate",
)


def transport_channel_id(
    transport, is_server: bool, channel_id_type: str | None = None
) -> bytes:
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
    :param channel_id_type: TLS channel ID type: ``"tls-unique"`` (RFC 5929, TLS <= 1.2)
        is supported. ``"tls-exporter"`` (RFC 9266, TLS 1.3) is not available on the
        asyncio backend - the Python stdlib ``ssl`` module does not expose it - and
        raises ``NotImplementedError``; use the Twisted backend for TLS 1.3 +
        ``tls-exporter``. See :ref:`tls-channel-binding` for the full support matrix.
    :returns: The TLS channel id (32 bytes).
    """
    if channel_id_type is None:
        return b"\x00" * 32

    if channel_id_type == "tls-exporter":
        # tls-exporter (RFC 9266) is TLS 1.3 exported keying material. The Python
        # stdlib ssl module exposes only "tls-unique" in ssl.CHANNEL_BINDING_TYPES
        # (through CPython 3.14), so the asyncio backend cannot compute it: fail fast
        # and point at the Twisted backend (pyOpenSSL), which does support it. Should
        # a future CPython add "tls-exporter" to ssl.CHANNEL_BINDING_TYPES, use it
        # directly - the exporter is already a 32-byte value per RFC 9266, so (unlike
        # tls-unique) it is returned raw, without hashing, matching the Twisted backend.
        if "tls-exporter" not in ssl.CHANNEL_BINDING_TYPES:
            raise NotImplementedError(
                "tls-exporter channel binding (RFC 9266) is not available on the "
                "asyncio backend: the Python stdlib ssl module exposes only "
                f"{list(ssl.CHANNEL_BINDING_TYPES)}. Use the Twisted backend for "
                "TLS 1.3 + tls-exporter."
            )
        ssl_obj = transport.get_extra_info("ssl_object")
        if ssl_obj is None:
            raise Exception(
                "TLS transport channel_id for tls-exporter requested, but ssl_obj not found on transport"
            )
        cb = ssl_obj.get_channel_binding("tls-exporter")
        if type(cb) != bytes:
            return b"\x00" * 32
        return cb

    # ssl.CHANNEL_BINDING_TYPES
    if channel_id_type not in ["tls-unique"]:
        raise Exception(f"invalid channel ID type {channel_id_type}")

    ssl_obj = transport.get_extra_info("ssl_object")
    if ssl_obj is None:
        raise Exception(
            "TLS transport channel_id for tls-unique requested, but ssl_obj not found on transport"
        )

    if not hasattr(ssl_obj, "get_channel_binding"):
        raise Exception(
            "TLS transport channel_id for tls-unique requested, but get_channel_binding not found on ssl_obj"
        )

    # tls-unique (RFC 5929) is only defined for TLS <= 1.2. On TLS 1.3 the stdlib ssl
    # module does not fail get_channel_binding("tls-unique"): it returns the (longer)
    # TLS 1.3 Finished message, which forms a non-standard binding that only happens to
    # match between two stdlib peers. Reject it explicitly on TLS 1.3 (#2078), so a TLS
    # 1.3 peer uses tls-exporter (RFC 9266, not available on the asyncio backend) or no
    # binding - never a bogus tls-unique.
    if ssl_obj.version() == "TLSv1.3":
        raise RuntimeError(
            "tls-unique channel binding (RFC 5929) is not defined for TLS 1.3; "
            "use tls-exporter (RFC 9266) on TLS 1.3"
        )

    # https://docs.python.org/3/library/ssl.html#ssl.SSLSocket.get_channel_binding
    # https://www.rfc-editor.org/rfc/rfc5929.html (and see tls_unique() on PyPy)
    tls_finished_msg = tls_unique(ssl_obj)

    if type(tls_finished_msg) != bytes:
        return b"\x00" * 32
    else:
        m = hashlib.sha256()
        m.update(tls_finished_msg)
        channel_id = m.digest()
        return channel_id


def create_tls_channel_id(transport, is_server: bool) -> dict[str, bytes]:
    """
    Build the TLS channel-binding map for an asyncio transport whose TLS opening handshake
    has completed, following the negotiated TLS version (hard split, #2078): tls-unique
    (RFC 5929) on TLS <= 1.2, tls-exporter (RFC 9266) on TLS 1.3.

    On the asyncio backend tls-exporter is not available (the stdlib ``ssl`` module exposes
    only tls-unique in ``ssl.CHANNEL_BINDING_TYPES`` through CPython 3.14), so on TLS 1.3 the
    map is empty today - an asyncio peer cannot channel-bind on TLS 1.3; use the Twisted
    backend (pyOpenSSL), or TLS <= 1.2. The ``ssl.CHANNEL_BINDING_TYPES`` guard activates
    tls-exporter automatically should a future CPython add it (symmetric with Twisted).

    :param transport: The asyncio TLS transport (post-handshake).
    :param is_server: Flag indicating this transport side is a server.
    :return: Channel-binding map: ``{"tls-unique": ...}`` on TLS <= 1.2 or ``{}`` (or
        ``{"tls-exporter": ...}`` on a future stdlib) on TLS 1.3.
    """
    ssl_obj = transport.get_extra_info("ssl_object", None)
    if ssl_obj is not None and ssl_obj.version() == "TLSv1.3":
        channel_id: dict[str, bytes] = {}
        if "tls-exporter" in ssl.CHANNEL_BINDING_TYPES:
            channel_id["tls-exporter"] = transport_channel_id(
                transport, is_server, "tls-exporter"
            )
        return channel_id
    return {
        "tls-unique": transport_channel_id(transport, is_server, "tls-unique"),
    }


def peer2str(transport: asyncio.transports.BaseTransport) -> str:
    # https://docs.python.org/3.9/library/asyncio-protocol.html?highlight=get_extra_info#asyncio.BaseTransport.get_extra_info
    # https://docs.python.org/3.9/library/socket.html#socket.socket.getpeername
    try:
        peer = transport.get_extra_info("peername")
        if isinstance(peer, tuple):
            ip_ver = 4 if len(peer) == 2 else 6
            return f"tcp{ip_ver}:{peer[0]}:{peer[1]}"
        elif isinstance(peer, str):
            return f"unix:{peer}"
        else:
            return f"?:{peer}"
    except:
        pass

    try:
        proc: Popen = transport.get_extra_info("subprocess")
        # return 'process:{}'.format(transport.pid)
        return f"process:{proc.pid}"
    except:
        pass

    try:
        pipe = transport.get_extra_info("pipe")
        return f"pipe:{pipe}"
    except:
        pass

    # gracefully fallback if we can't map the peer's transport
    return "unknown"


def get_serializers():
    from autobahn.wamp import serializer

    serializers = [
        "CBORSerializer",
        "MsgPackSerializer",
        "UBJSONSerializer",
        "JsonSerializer",
    ]
    serializers = list(
        filter(
            lambda x: x,
            map(
                lambda s: getattr(serializer, s) if hasattr(serializer, s) else None,
                serializers,
            ),
        )
    )
    return serializers


def extract_peer_certificate(ssl_obj) -> dict[str, Any] | None:
    """
    Extract information on the TLS peer certificate (if the peer presented one) from the
    SSL object of an asyncio TLS transport (see :func:`autobahn.util.peer_certificate_details`).

    :param ssl_obj: The ``ssl.SSLObject`` of the TLS transport.
    :returns: The certificate information, or ``None`` if the peer presented no certificate.
    """
    der = ssl_obj.getpeercert(binary_form=True)
    if not der or not isinstance(der, bytes):
        return None
    from cryptography import x509

    try:
        cert = x509.load_der_x509_certificate(der)
    except ValueError:
        # OpenSSL accepted the certificate in the TLS handshake, but cryptography cannot parse it
        return None
    return peer_certificate_details(cert)


def create_transport_details(transport, is_server: bool) -> TransportDetails:
    # Internal helper. Base class calls this to create a TransportDetails
    peer = peer2str(transport)

    # https://docs.python.org/3/library/asyncio-protocol.html#asyncio.BaseTransport.get_extra_info
    # a TLS connection has an SSL object, whether or not the peer presented a certificate
    # ("peercert" is only set for a peer certificate, so a server without client certificate
    # was not "secure" and had no channel ID, #2014)
    ssl_obj = transport.get_extra_info("ssl_object", None)
    is_secure = ssl_obj is not None
    if is_secure:
        # select the channel binding by negotiated TLS version (tls-unique on TLS <= 1.2,
        # tls-exporter on TLS 1.3 where available; empty on asyncio TLS 1.3 today, #2078)
        channel_id = create_tls_channel_id(transport, is_server)
        channel_type = TransportDetails.CHANNEL_TYPE_TLS
        peer_cert = extract_peer_certificate(ssl_obj)
    else:
        channel_id = {}
        channel_type = TransportDetails.CHANNEL_TYPE_TCP
        peer_cert = None
    channel_framing = TransportDetails.CHANNEL_FRAMING_WEBSOCKET

    return TransportDetails(
        channel_type=channel_type,
        channel_framing=channel_framing,
        peer=peer,
        is_server=is_server,
        is_secure=is_secure,
        channel_id=channel_id,
        peer_cert=peer_cert,
    )
