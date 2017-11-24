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

from __future__ import absolute_import

import os
import base64
import six
import struct
import time
import binascii
import hmac
import hashlib
import random
from struct import Struct
from operator import xor
from itertools import starmap
from autobahn.util import public
from autobahn.wamp.interfaces import IAuthenticator


__all__ = (
    'AuthCryptoSign',
    'AuthWampCra',
    'pbkdf2',
    'generate_totp_secret',
    'compute_totp',
    'derive_key',
    'generate_wcs',
    'compute_wcs',
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
            AuthWampCra.name: AuthWampCra,
            AuthCryptoSign.name: AuthCryptoSign,
            AuthAnonymous.name: AuthAnonymous,
            AuthTicket.name: AuthTicket,
        }[name]
    except KeyError:
        raise ValueError(
            "Unknown authenticator '{}'".format(name)
        )
    # this may raise further ValueErrors if the kwargs are wrong
    authenticator = klass(**kwargs)
    return authenticator


# experimental authentication API
class AuthAnonymous(object):
    name = u'anonymous'

    def __init__(self, **kw):
        self._args = kw

    @property
    def authextra(self):
        return self._args.get(u'authextra', dict())

    def on_challenge(self, session, challenge):
        raise RuntimeError(
            "on_challenge called on anonymous authentication"
        )


IAuthenticator.register(AuthAnonymous)


class AuthTicket(object):
    name = u'ticket'

    def __init__(self, **kw):
        self._args = kw
        try:
            self._ticket = self._args.pop(u'ticket')
        except KeyError:
            raise ValueError(
                "ticket authentication requires 'ticket=' kwarg"
            )

    @property
    def authextra(self):
        return self._args.get(u'authextra', dict())

    def on_challenge(self, session, challenge):
        assert challenge.method == u"ticket"
        return self._ticket


IAuthenticator.register(AuthTicket)


class AuthCryptoSign(object):
    name = u'cryptosign'

    def __init__(self, **kw):
        # should put in checkconfig or similar
        for key in kw.keys():
            if key not in [u'authextra', u'authid', u'authrole', u'privkey']:
                raise ValueError(
                    "Unexpected key '{}' for {}".format(key, self.__class__.__name__)
                )
        for key in [u'privkey', u'authid']:
            if key not in kw:
                raise ValueError(
                    "Must provide '{}' for cryptosign".format(key)
                )
        for key in kw.get('authextra', dict()):
            if key not in [u'pubkey']:
                raise ValueError(
                    "Unexpected key '{}' in 'authextra'".format(key)
                )

        from autobahn.wamp.cryptosign import SigningKey
        self._privkey = SigningKey.from_key_bytes(
            binascii.a2b_hex(kw[u'privkey'])
        )

        if u'pubkey' in kw.get(u'authextra', dict()):
            pubkey = kw[u'authextra'][u'pubkey']
            if pubkey != self._privkey.public_key():
                raise ValueError(
                    "Public key doesn't correspond to private key"
                )
        else:
            kw[u'authextra'] = kw.get(u'authextra', dict())
            kw[u'authextra'][u'pubkey'] = self._privkey.public_key()
        self._args = kw

    @property
    def authextra(self):
        return self._args.get(u'authextra', dict())

    def on_challenge(self, session, challenge):
        return self._privkey.sign_challenge(session, challenge)


IAuthenticator.register(AuthCryptoSign)


class AuthWampCra(object):
    name = u'wampcra'

    def __init__(self, **kw):
        # should put in checkconfig or similar
        for key in kw.keys():
            if key not in [u'authextra', u'authid', u'authrole', u'secret']:
                raise ValueError(
                    "Unexpected key '{}' for {}".format(key, self.__class__.__name__)
                )
        for key in [u'secret', u'authid']:
            if key not in kw:
                raise ValueError(
                    "Must provide '{}' for wampcra".format(key)
                )

        self._args = kw
        self._secret = kw.pop(u'secret')
        if not isinstance(self._secret, six.text_type):
            self._secret = self._secret.decode('utf8')

    @property
    def authextra(self):
        return self._args.get(u'authextra', dict())

    def on_challenge(self, session, challenge):
        key = self._secret.encode('utf8')
        if u'salt' in challenge.extra:
            key = derive_key(
                key,
                challenge.extra['salt'],
                challenge.extra['iterations'],
                challenge.extra['keylen']
            )

        signature = compute_wcs(
            key,
            challenge.extra['challenge'].encode('utf8')
        )
        return signature.decode('ascii')


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
    assert(type(length) in six.integer_types)
    return base64.b32encode(os.urandom(length)).decode('ascii')


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
    assert(type(secret) == six.text_type)
    assert(type(offset) in six.integer_types)
    try:
        key = base64.b32decode(secret)
    except TypeError:
        raise Exception('invalid secret')
    interval = offset + int(time.time()) // 30
    msg = struct.pack('>Q', interval)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    o = 15 & (digest[19] if six.PY3 else ord(digest[19]))
    token = (struct.unpack('>I', digest[o:o + 4])[0] & 0x7fffffff) % 1000000
    return u'{0:06d}'.format(token)


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
    if type(secret) != six.text_type:
        raise Exception('secret must be of type unicode, not {}'.format(type(secret)))

    if type(label) != six.text_type:
        raise Exception('label must be of type unicode, not {}'.format(type(label)))

    try:
        import pyqrcode
    except ImportError:
        raise Exception('pyqrcode not installed')

    import io
    buffer = io.BytesIO()

    data = pyqrcode.create(u'otpauth://totp/{}?secret={}&issuer={}'.format(label, secret, issuer))
    data.svg(buffer, omithw=True)

    return buffer.getvalue()


#
# The following code is adapted from the pbkdf2_bin() function
# in here https://github.com/mitsuhiko/python-pbkdf2
# Copyright 2011 by Armin Ronacher. Licensed under BSD license.
# https://github.com/mitsuhiko/python-pbkdf2/blob/master/LICENSE
#
_pack_int = Struct('>I').pack

if six.PY3:

    def _pseudorandom(x, mac):
        h = mac.copy()
        h.update(x)
        return h.digest()

    def _pbkdf2(data, salt, iterations, keylen, hashfunc):
        mac = hmac.new(data, None, hashfunc)
        buf = []
        for block in range(1, -(-keylen // mac.digest_size) + 1):
            rv = u = _pseudorandom(salt + _pack_int(block), mac)
            for i in range(iterations - 1):
                u = _pseudorandom(u, mac)
                rv = starmap(xor, zip(rv, u))
            buf.extend(rv)
        return bytes(buf)[:keylen]

else:
    from itertools import izip

    def _pseudorandom(x, mac):
        h = mac.copy()
        h.update(x)
        return map(ord, h.digest())

    def _pbkdf2(data, salt, iterations, keylen, hashfunc):
        mac = hmac.new(data, None, hashfunc)
        buf = []
        for block in range(1, -(-keylen // mac.digest_size) + 1):
            rv = u = _pseudorandom(salt + _pack_int(block), mac)
            for i in range(iterations - 1):
                u = _pseudorandom(''.join(map(chr, u)), mac)
                rv = starmap(xor, izip(rv, u))
            buf.extend(rv)
        return ''.join(map(chr, buf))[:keylen]


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
    :param hashfunc: The hash function to use, e.g. ``hashlib.sha1``.
    :type hashfunc: callable

    :returns: The derived cryptographic key.
    :rtype: bytes
    """
    assert(type(data) == bytes)
    assert(type(salt) == bytes)
    assert(type(iterations) in six.integer_types)
    assert(type(keylen) in six.integer_types)
    return _pbkdf2(data, salt, iterations, keylen, hashfunc or hashlib.sha256)


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
    assert(type(secret) in [six.text_type, six.binary_type])
    assert(type(salt) in [six.text_type, six.binary_type])
    assert(type(iterations) in six.integer_types)
    assert(type(keylen) in six.integer_types)
    if type(secret) == six.text_type:
        secret = secret.encode('utf8')
    if type(salt) == six.text_type:
        salt = salt.encode('utf8')
    key = pbkdf2(secret, salt, iterations, keylen)
    return binascii.b2a_base64(key).strip()


WCS_SECRET_CHARSET = u"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
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
    assert(type(length) in six.integer_types)
    return u"".join([random.choice(WCS_SECRET_CHARSET) for _ in range(length)]).encode('ascii')


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
    assert(type(key) in [six.text_type, six.binary_type])
    assert(type(challenge) in [six.text_type, six.binary_type])
    if type(key) == six.text_type:
        key = key.encode('utf8')
    if type(challenge) == six.text_type:
        challenge = challenge.encode('utf8')
    sig = hmac.new(key, challenge, hashlib.sha256).digest()
    return binascii.b2a_base64(sig).strip()
