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

import base64
import binascii
import hashlib
import hmac
import os
import random
import struct
import time
from typing import Dict, Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from autobahn.util import public
from autobahn.util import xor as xor_array
from autobahn.wamp.interfaces import IAuthenticator

# if we don't have argon2/passlib (see "authentication" extra) then
# you don't get AuthScram and variants
try:
    from argon2 import Type
    from argon2.low_level import hash_secret
    from passlib.utils import saslprep

    HAS_ARGON = True
except ImportError:
    HAS_ARGON = False


__all__ = (
    "AuthAnonymous",
    "AuthCryptoSign",
    "AuthScram",
    "AuthTicket",
    "AuthWampCra",
    "check_totp",
    "compute_totp",
    "compute_wcs",
    "create_authenticator",
    "derive_key",
    "derive_scram_credential",
    "generate_totp_secret",
    "generate_wcs",
    "pbkdf2",
    "qrcode_from_totp",
)


def create_authenticator(name, **kwargs):
    """
    Accepts various keys and values to configure an authenticator. The
    valid keys depend on the kind of authenticator but all can
    understand: `authextra`, `authid` and `authrole`

    :return: an instance implementing IAuthenticator with the given
        configuration.
    """
    try:
        klass = {
            AuthScram.name: AuthScram,
            AuthCryptoSign.name: AuthCryptoSign,
            AuthCryptoSignProxy.name: AuthCryptoSignProxy,
            AuthWampCra.name: AuthWampCra,
            AuthAnonymous.name: AuthAnonymous,
            AuthAnonymousProxy.name: AuthAnonymousProxy,
            AuthTicket.name: AuthTicket,
        }[name]
    except KeyError:
        raise ValueError("Unknown authenticator '{}'".format(name))
    # this may raise further ValueErrors if the kwargs are wrong
    authenticator = klass(**kwargs)
    return authenticator


# experimental authentication API
class AuthAnonymous(object):
    name = "anonymous"

    def __init__(self, **kw):
        self._args = kw

    @property
    def authextra(self):
        return self._args.get("authextra", dict())

    def on_challenge(self, session, challenge):
        raise RuntimeError("on_challenge called on anonymous authentication")

    def on_welcome(self, msg, authextra):
        return None


IAuthenticator.register(AuthAnonymous)


class AuthAnonymousProxy(AuthAnonymous):
    name = "anonymous-proxy"


IAuthenticator.register(AuthAnonymousProxy)


class AuthTicket(object):
    name = "ticket"

    def __init__(self, **kw):
        self._args = kw
        try:
            self._ticket = self._args.pop("ticket")
        except KeyError:
            raise ValueError("ticket authentication requires 'ticket=' kwarg")

    @property
    def authextra(self):
        return self._args.get("authextra", dict())

    def on_challenge(self, session, challenge):
        assert challenge.method == "ticket"
        return self._ticket

    def on_welcome(self, msg, authextra):
        return None


IAuthenticator.register(AuthTicket)


class AuthCryptoSign(object):
    name = "cryptosign"

    def __init__(self, **kw):
        # should put in checkconfig or similar
        for key in kw.keys():
            if key not in ["authextra", "authid", "authrole", "privkey"]:
                raise ValueError(
                    "Unexpected key '{}' for {}".format(key, self.__class__.__name__)
                )
        for key in ["privkey"]:
            if key not in kw:
                raise ValueError("Must provide '{}' for cryptosign".format(key))

        from autobahn.wamp.cryptosign import CryptosignKey

        self._privkey = CryptosignKey.from_bytes(binascii.a2b_hex(kw["privkey"]))

        if "pubkey" in kw.get("authextra", dict()):
            pubkey = kw["authextra"]["pubkey"]
            if pubkey != self._privkey.public_key():
                raise ValueError("Public key doesn't correspond to private key")
        else:
            kw["authextra"] = kw.get("authextra", dict())
            kw["authextra"]["pubkey"] = self._privkey.public_key()

        self._channel_binding = kw.get("authextra", dict()).get("channel_binding", None)
        self._args = kw

    @property
    def authextra(self):
        return self._args.get("authextra", dict())

    def on_challenge(self, session, challenge):
        channel_id = session._transport.transport_details.channel_id.get(
            self._channel_binding, None
        )
        return self._privkey.sign_challenge(
            challenge, channel_id=channel_id, channel_id_type=self._channel_binding
        )

    def on_welcome(self, msg, authextra):
        return None


IAuthenticator.register(AuthCryptoSign)


class AuthCryptoSignProxy(AuthCryptoSign):
    name = "cryptosign-proxy"


IAuthenticator.register(AuthCryptoSignProxy)


def _hash_argon2id13_secret(password, salt, iterations, memory):
    """
    Internal helper. Returns the salted/hashed password using the
    argon2id-13 algorithm. The return value is base64-encoded.
    """
    rawhash = hash_secret(
        secret=password,
        salt=base64.b64decode(salt),
        time_cost=iterations,
        memory_cost=memory,
        parallelism=1,  # hard-coded by WAMP-SCRAM spec
        hash_len=32,
        type=Type.ID,
        version=0x13,  # note this is decimal "19" which appears in places
    )
    # spits out stuff like:
    # '$argon2i$v=19$m=512,t=2,p=2$5VtWOO3cGWYQHEMaYGbsfQ$AcmqasQgW/wI6wAHAMk4aQ'

    _, tag, ver, options, salt_data, hash_data = rawhash.split(b"$")
    return hash_data


def _hash_pbkdf2_secret(password, salt, iterations):
    """
    Internal helper for SCRAM authentication
    """
    return pbkdf2(password, salt, iterations, keylen=32)


class AuthScram(object):
    """
    Implements "wamp-scram" authentication for components.

    NOTE: This is a prototype of a draft spec; see
    https://github.com/wamp-proto/wamp-proto/issues/135
    """

    name = "scram"

    def __init__(self, **kw):
        if not HAS_ARGON:
            raise RuntimeError(
                "Cannot support WAMP-SCRAM without argon2_cffi and "
                "passlib libraries; install autobahn['scram']"
            )
        self._args = kw
        self._client_nonce = None

    @property
    def authextra(self):
        # is authextra() called exactly once per authentication?
        if self._client_nonce is None:
            self._client_nonce = base64.b64encode(os.urandom(16)).decode("ascii")
        return {
            "nonce": self._client_nonce,
        }

    def on_challenge(self, session, challenge):
        assert challenge.method == "scram"
        assert self._client_nonce is not None
        required_args = ["nonce", "kdf", "salt", "iterations"]
        optional_args = ["memory", "channel_binding"]
        for k in required_args:
            if k not in challenge.extra:
                raise RuntimeError(
                    "WAMP-SCRAM challenge option '{}' is "
                    " required but not specified".format(k)
                )
        for k in challenge.extra:
            if k not in optional_args + required_args:
                raise RuntimeError(
                    "WAMP-SCRAM challenge has unknown attribute '{}'".format(k)
                )

        channel_binding = challenge.extra.get("channel_binding", "")
        server_nonce = challenge.extra["nonce"]  # base64
        salt = challenge.extra["salt"]  # base64
        iterations = int(challenge.extra["iterations"])
        memory = int(challenge.extra.get("memory", -1))
        password = self._args["password"].encode("utf8")  # supplied by user
        authid = saslprep(self._args["authid"])
        algorithm = challenge.extra["kdf"]
        client_nonce = self._client_nonce

        self._auth_message = (
            "{client_first_bare},{server_first},{client_final_no_proof}".format(
                client_first_bare="n={},r={}".format(authid, client_nonce),
                server_first="r={},s={},i={}".format(server_nonce, salt, iterations),
                client_final_no_proof="c={},r={}".format(channel_binding, server_nonce),
            )
        ).encode("ascii")

        if algorithm == "argon2id-13":
            if memory == -1:
                raise ValueError(
                    "WAMP-SCRAM 'argon2id-13' challenge requires 'memory' parameter"
                )
            self._salted_password = _hash_argon2id13_secret(
                password, salt, iterations, memory
            )
        elif algorithm == "pbkdf2":
            self._salted_password = _hash_pbkdf2_secret(password, salt, iterations)
        else:
            raise RuntimeError(
                "WAMP-SCRAM specified unknown KDF '{}'".format(algorithm)
            )

        client_key = hmac.new(
            self._salted_password, b"Client Key", hashlib.sha256
        ).digest()
        stored_key = hashlib.new("sha256", client_key).digest()

        client_signature = hmac.new(
            stored_key, self._auth_message, hashlib.sha256
        ).digest()
        client_proof = xor_array(client_key, client_signature)

        return base64.b64encode(client_proof)

    def on_welcome(self, session, authextra):
        """
        When the server is satisfied, it sends a 'WELCOME' message.

        This hook allows us an opportunity to deny the session right
        before it gets set up -- we check the server-signature thus
        authorizing the server and if it fails we drop the connection.
        """
        alleged_server_sig = base64.b64decode(authextra["scram_server_signature"])
        server_key = hmac.new(
            self._salted_password, b"Server Key", hashlib.sha256
        ).digest()
        server_signature = hmac.new(
            server_key, self._auth_message, hashlib.sha256
        ).digest()
        if not hmac.compare_digest(server_signature, alleged_server_sig):
            session.log.error("Verification of server SCRAM signature failed")
            return "Verification of server SCRAM signature failed"
        session.log.info("Verification of server SCRAM signature successful")
        return None


IAuthenticator.register(AuthScram)


class AuthWampCra(object):
    name = "wampcra"

    def __init__(self, **kw):
        # should put in checkconfig or similar
        for key in kw.keys():
            if key not in ["authextra", "authid", "authrole", "secret"]:
                raise ValueError(
                    "Unexpected key '{}' for {}".format(key, self.__class__.__name__)
                )
        for key in ["secret", "authid"]:
            if key not in kw:
                raise ValueError("Must provide '{}' for wampcra".format(key))

        self._args = kw
        self._secret = kw.pop("secret")
        if not isinstance(self._secret, str):
            self._secret = self._secret.decode("utf8")

    @property
    def authextra(self):
        return self._args.get("authextra", dict())

    def on_challenge(self, session, challenge):
        key = self._secret.encode("utf8")
        if "salt" in challenge.extra:
            key = derive_key(
                key,
                challenge.extra["salt"],
                challenge.extra["iterations"],
                challenge.extra["keylen"],
            )

        signature = compute_wcs(key, challenge.extra["challenge"].encode("utf8"))
        return signature.decode("ascii")

    def on_welcome(self, msg, authextra):
        return None


IAuthenticator.register(AuthWampCra)


@public
def generate_totp_secret(length=10):
    """
    Generates a new Base32 encoded, random secret.

    .. seealso:: http://en.wikipedia.org/wiki/Base32

    :param length: The length of the entropy used to generate the secret.
    :type length: int

    :returns: The generated secret in Base32 (letters ``A-Z`` and digits ``2-7``).
       The length of the generated secret is ``length * 8 / 5`` octets.
    :rtype: unicode
    """
    assert type(length) == int
    return base64.b32encode(os.urandom(length)).decode("ascii")


@public
def compute_totp(secret, offset=0):
    """
    Computes the current TOTP code.

    :param secret: Base32 encoded secret.
    :type secret: unicode
    :param offset: Time offset (in steps, use eg -1, 0, +1 for compliance with RFC6238)
        for which to compute TOTP.
    :type offset: int

    :returns: TOTP for current time (+/- offset).
    :rtype: unicode
    """
    assert type(secret) == str
    assert type(offset) == int
    try:
        key = base64.b32decode(secret)
    except TypeError:
        raise Exception("invalid secret")
    interval = offset + int(time.time()) // 30
    msg = struct.pack(">Q", interval)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    o = 15 & (digest[19])
    token = (struct.unpack(">I", digest[o : o + 4])[0] & 0x7FFFFFFF) % 1000000
    return "{0:06d}".format(token)


@public
def check_totp(secret, ticket):
    """
    Check a TOTP value received from a principal trying to authenticate against
    the expected value computed from the secret shared between the principal and
    the authenticating entity.

    The Internet can be slow, and clocks might not match exactly, so some
    leniency is allowed. RFC6238 recommends looking an extra time step in either
    direction, which essentially opens the window from 30 seconds to 90 seconds.

    :param secret: The secret shared between the principal (eg a client) that
        is authenticating, and the authenticating entity (eg a server).
    :type secret: unicode
    :param ticket: The TOTP value to be checked.
    :type ticket: unicode

    :returns: ``True`` if the TOTP value is correct, else ``False``.
    :rtype: bool
    """
    for offset in [0, 1, -1]:
        if ticket == compute_totp(secret, offset):
            return True
    return False


@public
def qrcode_from_totp(secret, label, issuer):
    if type(secret) != str:
        raise Exception("secret must be of type unicode, not {}".format(type(secret)))

    if type(label) != str:
        raise Exception("label must be of type unicode, not {}".format(type(label)))

    try:
        import qrcode
        import qrcode.image.svg
    except ImportError:
        raise Exception("qrcode not installed")

    return qrcode.make(
        "otpauth://totp/{}?secret={}&issuer={}".format(label, secret, issuer),
        box_size=3,
        image_factory=qrcode.image.svg.SvgImage,
    ).to_string()


@public
def pbkdf2(data, salt, iterations=1000, keylen=32, hashfunc=None):
    """
    Returns a binary digest for the PBKDF2 hash algorithm of ``data``
    with the given ``salt``. It iterates ``iterations`` time and produces a
    key of ``keylen`` bytes. By default SHA-256 is used as hash function,
    a different hashlib ``hashfunc`` can be provided.

    :param data: The data for which to compute the PBKDF2 derived key.
    :type data: bytes
    :param salt: The salt to use for deriving the key.
    :type salt: bytes
    :param iterations: The number of iterations to perform in PBKDF2.
    :type iterations: int
    :param keylen: The length of the cryptographic key to derive.
    :type keylen: int
    :param hashfunc: Name of the hash algorithm to use
    :type hashfunc: str

    :returns: The derived cryptographic key.
    :rtype: bytes
    """
    if (
        not (type(data) == bytes)
        or not (type(salt) == bytes)
        or not (type(iterations) == int)
        or not (type(keylen) == int)
    ):
        raise ValueError("Invalid argument types")

    # justification: WAMP-CRA uses SHA256 and users shouldn't have any
    # other reason to call this particular pbkdf2 function (arguably,
    # it should be private maybe?)
    if hashfunc is None:
        hashfunc = "sha256"
    if hashfunc is callable:
        # used to take stuff from hashlib; translate?
        raise ValueError(
            "pbkdf2 now takes the name of a hash algorithm for 'hashfunc='"
        )

    backend = default_backend()

    # https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#pbkdf2
    kdf = PBKDF2HMAC(
        algorithm=getattr(hashes, hashfunc.upper())(),
        length=keylen,
        salt=salt,
        iterations=iterations,
        backend=backend,
    )
    return kdf.derive(data)


@public
def derive_key(secret, salt, iterations=1000, keylen=32):
    """
    Computes a derived cryptographic key from a password according to PBKDF2.

    .. seealso:: http://en.wikipedia.org/wiki/PBKDF2

    :param secret: The secret.
    :type secret: bytes or unicode
    :param salt: The salt to be used.
    :type salt: bytes or unicode
    :param iterations: Number of iterations of derivation algorithm to run.
    :type iterations: int
    :param keylen: Length of the key to derive in bytes.
    :type keylen: int

    :return: The derived key in Base64 encoding.
    :rtype: bytes
    """
    if not (type(secret) in [str, bytes]):
        raise ValueError("'secret' must be bytes")
    if not (type(salt) in [str, bytes]):
        raise ValueError("'salt' must be bytes")
    if not (type(iterations) == int):
        raise ValueError("'iterations' must be an integer")
    if not (type(keylen) == int):
        raise ValueError("'keylen' must be an integer")
    if type(secret) == str:
        secret = secret.encode("utf8")
    if type(salt) == str:
        salt = salt.encode("utf8")
    key = pbkdf2(secret, salt, iterations, keylen)
    return binascii.b2a_base64(key).strip()


WCS_SECRET_CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
"""
The characters from which :func:`autobahn.wamp.auth.generate_wcs` generates secrets.
"""


@public
def generate_wcs(length=14):
    """
    Generates a new random secret for use with WAMP-CRA.

    The secret generated is a random character sequence drawn from

    - upper and lower case latin letters
    - digits
    -

    :param length: The length of the secret to generate.
    :type length: int

    :return: The generated secret. The length of the generated is ``length`` octets.
    :rtype: bytes
    """
    assert type(length) == int
    return "".join(random.choice(WCS_SECRET_CHARSET) for _ in range(length)).encode(
        "ascii"
    )


@public
def compute_wcs(key, challenge):
    """
    Compute an WAMP-CRA authentication signature from an authentication
    challenge and a (derived) key.

    :param key: The key derived (via PBKDF2) from the secret.
    :type key: bytes
    :param challenge: The authentication challenge to sign.
    :type challenge: bytes

    :return: The authentication signature.
    :rtype: bytes
    """
    assert type(key) in [str, bytes]
    assert type(challenge) in [str, bytes]
    if type(key) == str:
        key = key.encode("utf8")
    if type(challenge) == str:
        challenge = challenge.encode("utf8")
    sig = hmac.new(key, challenge, hashlib.sha256).digest()
    return binascii.b2a_base64(sig).strip()


def derive_scram_credential(
    email: str, password: str, salt: Optional[bytes] = None
) -> Dict:
    """
    Derive WAMP-SCRAM credentials from user email and password. The SCRAM parameters used
    are the following (these are also contained in the returned credentials):

    * kdf ``argon2id-13``
    * time cost ``4096``
    * memory cost ``512``
    * parallelism ``1``

    See `draft-irtf-cfrg-argon2 <https://datatracker.ietf.org/doc/draft-irtf-cfrg-argon2/>`__ and
    `argon2-cffi <https://argon2-cffi.readthedocs.io/en/stable/>`__.

    :param email: User email.
    :param password: User password.
    :param salt: Optional salt to use (must be 16 bytes long). If none is given, compute salt
        from email as ``salt = SHA256(email)[:16]``.
    :return: WAMP-SCRAM credentials. When serialized, the returned credentials can be copy-pasted
        into the ``config.json`` node configuration for a Crossbar.io node.
    """
    assert HAS_ARGON, "missing dependency argon2"
    from argon2.low_level import Type, hash_secret

    # derive salt from email
    if not salt:
        m = hashlib.sha256()
        m.update(email.encode("utf8"))
        salt = m.digest()[:16]
    assert len(salt) == 16

    hash_data = hash_secret(
        secret=password.encode("utf8"),
        salt=salt,
        time_cost=4096,
        memory_cost=512,
        parallelism=1,
        hash_len=32,
        type=Type.ID,
        version=19,
    )
    _, tag, v, params, _, salted_password = hash_data.decode("ascii").split("$")
    assert tag == "argon2id"
    assert (
        v == "v=19"
    )  # argon's version 1.3 is represented as 0x13, which is 19 decimal...
    params = {k: v for k, v in [x.split("=") for x in params.split(",")]}

    salted_password = salted_password.encode("ascii")
    client_key = hmac.new(salted_password, b"Client Key", hashlib.sha256).digest()
    stored_key = hashlib.new("sha256", client_key).digest()
    server_key = hmac.new(salted_password, b"Server Key", hashlib.sha256).digest()

    credential = {
        "kdf": "argon2id-13",
        "memory": int(params["m"]),
        "iterations": int(params["t"]),
        "salt": binascii.b2a_hex(salt).decode("ascii"),
        "stored-key": binascii.b2a_hex(stored_key).decode("ascii"),
        "server-key": binascii.b2a_hex(server_key).decode("ascii"),
    }
    return credential
