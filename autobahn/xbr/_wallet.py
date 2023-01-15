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
from typing import Optional
import argon2
import hkdf


def stretch_argon2_secret(email: str, password: str, salt: Optional[bytes] = None) -> bytes:
    """
    Compute argon2id based secret from user email and password only. This uses Argon2id
    for stretching a potentially weak user password/PIN and subsequent HKDF based key
    extending to derive private key material (PKM) for different usage contexts.

    The Argon2 parameters used are the following:

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
    :return: The computed private key material (256b, 32 octets).
    """
    if not salt:
        m = hashlib.sha256()
        m.update(email.encode('utf8'))
        salt = m.digest()[:16]
    assert len(salt) == 16

    pkm = argon2.low_level.hash_secret_raw(
        secret=password.encode('utf8'),
        salt=salt,
        time_cost=4096,
        memory_cost=512,
        parallelism=1,
        hash_len=32,
        type=argon2.low_level.Type.ID,
        version=19,
    )

    return pkm


def expand_argon2_secret(pkm: bytes, context: bytes, salt: Optional[bytes] = None) -> bytes:
    """

    Expand ``pkm`` and ``context`` into a key of length ``bytes`` using
    HKDF's expand function based on HMAC SHA-512). See the HKDF draft RFC and paper for usage notes.

    :param pkm:
    :param context:
    :param salt:
    :return:
    """
    kdf = hkdf.Hkdf(salt=salt, input_key_material=pkm, hash=hashlib.sha512)
    key = kdf.expand(info=context, length=32)
    return key


def pkm_from_argon2_secret(email: str, password: str, context: str, salt: Optional[bytes] = None) -> bytes:
    """

    :param email:
    :param password:
    :param context:
    :param salt:
    :return:
    """
    if not salt:
        m = hashlib.sha256()
        m.update(email.encode('utf8'))
        salt = m.digest()[:16]
    assert len(salt) == 16

    context = context.encode('utf8')

    pkm = stretch_argon2_secret(email=email, password=password, salt=salt)
    key = expand_argon2_secret(pkm=pkm, context=context, salt=salt)

    return key
