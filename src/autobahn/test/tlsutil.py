###############################################################################
#
#  Copyright (C) typedef int GmbH
#  SPDX-License-Identifier: MIT
#
###############################################################################
"""
Test helpers for WAMP over TLS (#2014), shared by the Twisted and the asyncio tests.

This module imports neither Twisted nor asyncio networking code: it only creates
certificates (with ``cryptography``) and provides the router side of a WAMP session
for authentication tests.
"""

import binascii
import datetime
import hashlib
import os

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from autobahn import util
from autobahn.wamp import message, role

# a subject with all the attribute types a client certificate typically carries
CLIENT_SUBJECT = {
    "c": "DE",
    "st": "Bavaria",
    "l": "Erlangen",
    "o": "Example GmbH",
    "ou": "Testing",
    "emailaddress": "client@example.com",
}

_NAME_OIDS = {
    "c": NameOID.COUNTRY_NAME,
    "st": NameOID.STATE_OR_PROVINCE_NAME,
    "l": NameOID.LOCALITY_NAME,
    "o": NameOID.ORGANIZATION_NAME,
    "ou": NameOID.ORGANIZATIONAL_UNIT_NAME,
    "cn": NameOID.COMMON_NAME,
    "emailaddress": NameOID.EMAIL_ADDRESS,
}


def _name(attrs):
    return x509.Name([x509.NameAttribute(_NAME_OIDS[k], v) for k, v in attrs.items()])


def fingerprint(cert, algorithm):
    """
    Fingerprint of a certificate as ``AA:BB:..`` (upper case hex), computed from its DER encoding.
    """
    digest = hashlib.new(
        algorithm, cert.public_bytes(serialization.Encoding.DER)
    ).digest()
    return ":".join(f"{b:02X}" for b in digest)


def _make_cert(subject, issuer_name, issuer_key, key, extensions, serial=None):
    now = datetime.datetime.now(datetime.UTC)
    builder = x509.CertificateBuilder(
        issuer_name=issuer_name,
        subject_name=subject,
        public_key=key.public_key(),
        serial_number=serial or x509.random_serial_number(),
        not_valid_before=(now - datetime.timedelta(days=1)).replace(microsecond=0),
        not_valid_after=(now + datetime.timedelta(days=1)).replace(microsecond=0),
        extensions=extensions,
    )
    return builder.sign(issuer_key, hashes.SHA256())


class ExamplePKI:
    """
    A certificate authority, a server certificate for ``localhost``, and client certificates
    ``client_0`` and ``client_1`` issued by it (as in the crossbar-examples TLS authentication
    example), written as PEM files to a directory.
    """

    def __init__(self, certdir):
        os.makedirs(certdir, exist_ok=True)
        self.certdir = certdir

        self.ca_key = ec.generate_private_key(ec.SECP256R1())
        self.ca_name = _name({"o": "Example GmbH", "cn": "Example Test CA"})
        self.ca_cert = _make_cert(
            self.ca_name,
            self.ca_name,
            self.ca_key,
            self.ca_key,
            [
                x509.Extension(
                    x509.BasicConstraints.oid,
                    True,
                    x509.BasicConstraints(ca=True, path_length=None),
                ),
                x509.Extension(
                    x509.KeyUsage.oid,
                    True,
                    x509.KeyUsage(
                        False, False, False, False, False, True, True, False, False
                    ),
                ),
            ],
        )
        self._write("ca", self.ca_key, self.ca_cert)

        self.server_key = ec.generate_private_key(ec.SECP256R1())
        self.server_cert = _make_cert(
            _name({"cn": "localhost"}),
            self.ca_name,
            self.ca_key,
            self.server_key,
            [
                x509.Extension(
                    x509.SubjectAlternativeName.oid,
                    False,
                    x509.SubjectAlternativeName([x509.DNSName("localhost")]),
                ),
            ],
        )
        self._write("server", self.server_key, self.server_cert)

        self.client_keys = {}
        self.client_certs = {}
        for name in ["client_0", "client_1"]:
            key = ec.generate_private_key(ec.SECP256R1())
            cert = _make_cert(
                _name(dict(CLIENT_SUBJECT, cn=name)),
                self.ca_name,
                self.ca_key,
                key,
                self.client_extensions(name),
            )
            self.client_keys[name] = key
            self.client_certs[name] = cert
            self._write(name, key, cert)

    @staticmethod
    def client_extensions(name):
        """
        The extensions of a client certificate: SAN, key usage (critical), extended key usage.
        """
        return [
            x509.Extension(
                x509.SubjectAlternativeName.oid,
                False,
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName(name),
                        x509.RFC822Name(CLIENT_SUBJECT["emailaddress"]),
                    ]
                ),
            ),
            x509.Extension(
                x509.KeyUsage.oid,
                True,
                x509.KeyUsage(
                    True, False, False, False, False, False, False, False, False
                ),
            ),
            x509.Extension(
                x509.ExtendedKeyUsage.oid,
                False,
                x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]),
            ),
        ]

    def duplicate_extension_cert(self):
        """
        A client certificate with its SAN extension twice: OpenSSL accepts it, ``cryptography``
        refuses to parse its extensions (``DuplicateExtension``).
        """
        key = ec.generate_private_key(ec.SECP256R1())
        san = self.client_extensions("client_dup")[0]
        return _make_cert(
            _name(dict(CLIENT_SUBJECT, cn="client_dup")),
            self.ca_name,
            self.ca_key,
            key,
            [san, san],
        )

    def path(self, name, kind):
        return os.path.join(self.certdir, f"{name}.{kind}")

    def pem(self, name, kind):
        with open(self.path(name, kind), "rb") as f:
            return f.read()

    def _write(self, name, key, cert):
        with open(self.path(name, "key"), "wb") as f:
            f.write(
                key.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.TraditionalOpenSSL,
                    serialization.NoEncryption(),
                )
            )
        with open(self.path(name, "crt"), "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))


def expected_peer_cert(cert, subject, issuer):
    """
    The ``TransportDetails.peer_cert`` dict expected for a certificate, for the fields whose
    format does not depend on the implementation. ``subject`` and ``issuer`` are the attributes
    as given when creating the certificate (OpenSSL short names, lower case).
    """
    return {
        "md5": fingerprint(cert, "md5"),
        "sha1": fingerprint(cert, "sha1"),
        "sha256": fingerprint(cert, "sha256"),
        "expired": False,
        "serial": cert.serial_number,
        "signature_algorithm": "ecdsa-with-SHA256",
        "version": 2,
        "not_before": cert.not_valid_before_utc.strftime("%Y%m%d%H%M%SZ"),
        "not_after": cert.not_valid_after_utc.strftime("%Y%m%d%H%M%SZ"),
        "subject": subject,
        "issuer": issuer,
    }


class FakeRouterSession:
    """
    The router side of a WAMP session (``ITransportHandler``), doing only what a router does to
    authenticate a client:

    * ``tls``: accept the client if the SHA1 fingerprint of its TLS client certificate
      (``transport_details.peer_cert["sha1"]``) is a known principal, as Crossbar.io's
      ``PendingAuthTLS`` does.
    * ``cryptosign``: send a challenge and verify the signature; with
      ``channel_binding="tls-unique"`` the signed message is the challenge XOR the TLS channel ID
      of the router side of the connection, as in Crossbar.io's ``PendingAuthCryptosign``.
      Unlike Crossbar.io, it denies the client when the channel binding is requested but the
      router has no channel ID, instead of falling back to no channel binding.

    ``observed`` collects ``(event, transport_details)`` pairs, and the reason of any ABORT;
    ``on_close`` is called when the transport is closed.
    """

    ZERO_CHANNEL_ID = b"\x00" * 32

    def __init__(self, principals=None, pubkeys=None, observed=None, on_close=None):
        self._principals = principals or {}
        self._pubkeys = pubkeys or {}
        self.observed = observed if observed is not None else []
        self._transport = None
        self._pending = None
        self._on_close = on_close
        # read by the WAMP transports (for logging)
        self._authid = None
        self._session_id = None

    def onOpen(self, transport):
        self._transport = transport
        self.observed.append(("open", transport.transport_details))

    def onMessage(self, msg):
        if isinstance(msg, message.Hello):
            td = self._transport.transport_details
            self.observed.append(("hello", td))
            if "tls" in msg.authmethods:
                self._hello_tls(td)
            elif "cryptosign" in msg.authmethods:
                self._hello_cryptosign(msg, td)
            else:
                self._abort("wamp.error.no_auth_method", "no supported authmethod")
        elif isinstance(msg, message.Authenticate) and self._pending:
            self._authenticate(msg)
        elif isinstance(msg, message.Goodbye):
            self._transport.send(message.Goodbye())
            self._transport.close()

    def onClose(self, wasClean):
        self.observed.append(("close", None))
        if self._on_close:
            self._on_close()

    def _hello_tls(self, td):
        peer_cert = td.peer_cert
        if not peer_cert:
            self._abort("wamp.error.not_authorized", "no client certificate presented")
        elif peer_cert.get("sha1") not in self._principals:
            self._abort(
                "wamp.error.not_authorized",
                "client certificate {} not accepted".format(peer_cert.get("sha1")),
            )
        else:
            authid, authrole = self._principals[peer_cert["sha1"]]
            self._welcome(authid, authrole, "tls")

    def _hello_cryptosign(self, msg, td):
        pubkey = (msg.authextra or {}).get("pubkey")
        if pubkey not in self._pubkeys:
            self._abort("wamp.error.not_authorized", "unknown public key")
            return
        channel_binding = msg.authextra.get("channel_binding")
        challenge = os.urandom(32)
        if channel_binding == "tls-unique":
            channel_id = td.channel_id.get("tls-unique") if td.channel_id else None
            if not channel_id or channel_id == self.ZERO_CHANNEL_ID:
                self._abort(
                    "wamp.error.not_authorized",
                    "channel binding requested, but no TLS channel ID",
                )
                return
            expected = util.xor(challenge, channel_id)
        else:
            expected = challenge
        self._pending = (pubkey, expected)
        extra = {
            "challenge": binascii.b2a_hex(challenge).decode(),
            "channel_binding": channel_binding,
        }
        self._transport.send(message.Challenge("cryptosign", extra))

    def _authenticate(self, msg):
        from nacl.exceptions import BadSignatureError
        from nacl.signing import VerifyKey

        pubkey, expected = self._pending
        self._pending = None
        try:
            signed = VerifyKey(binascii.a2b_hex(pubkey)).verify(
                binascii.a2b_hex(msg.signature)
            )
        except BadSignatureError:
            self._abort("wamp.error.not_authorized", "invalid signature")
            return
        if signed != expected:
            self._abort(
                "wamp.error.not_authorized",
                "signed message does not match the TLS channel",
            )
            return
        authid, authrole = self._pubkeys[pubkey]
        self._welcome(authid, authrole, "cryptosign")

    def _welcome(self, authid, authrole, authmethod):
        roles = {
            "broker": role.RoleBrokerFeatures(),
            "dealer": role.RoleDealerFeatures(),
        }
        self._authid = authid
        self._session_id = util.id()
        self._transport.send(
            message.Welcome(
                self._session_id,
                roles,
                authid=authid,
                authrole=authrole,
                authmethod=authmethod,
                authprovider="static",
            )
        )

    def _abort(self, reason, msg):
        self.observed.append(("abort", msg))
        self._transport.send(message.Abort(reason, msg))
