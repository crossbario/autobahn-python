###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

from __future__ import absolute_import

__all__ = (
   'generate_totp_secret',
   'compute_totp',
   'derive_key',
   'WCS_SECRET_CHARSET',
   'generate_wcs',
   'compute_wcs')

import os
import base64
import six
import struct
import time
import binascii



def generate_totp_secret(length = 10):
   """
   Generates a new Base32 encoded, random secret.

   .. seealso:: http://en.wikipedia.org/wiki/Base32

   :param length: The length of the entropy used to generate the secret.
   :type length: int

   :returns: The generated secret in Base32 (letters ``A-Z`` and digits ``2-7``).
      The length of the generated secret is ``length * 8 / 5`` octets.
   :rtype: bytes
   """
   assert(type(length) in six.integer_types)
   return base64.b32encode(os.urandom(length))



def compute_totp(secret, offset = 0):
   """
   Computes the current TOTP code.

   :param secret: Base32 encoded secret.
   :type secret: bytes
   :param offset: Time offset for which to compute TOTP.
   :type offset: int

   :returns: TOTP for current time (+/- offset).
   :rtype: bytes
   """
   assert(type(secret) == bytes)
   assert(type(offset) in six.integer_types)
   try:
      key = base64.b32decode(secret)
   except TypeError:
      raise Exception('invalid secret')
   interval = offset + int(time.time()) // 30
   msg = struct.pack('>Q', interval)
   digest = hmac.new(key, msg, hashlib.sha1).digest()
   o = 15 & (digest[19] if six.PY3 else ord(digest[19]))
   token = (struct.unpack('>I', digest[o:o+4])[0] & 0x7fffffff) % 1000000
   return '{:06d}'.format(token).encode('ascii')



## pbkdf2_bin() function taken from https://github.com/mitsuhiko/python-pbkdf2
## Copyright 2011 by Armin Ronacher. Licensed under BSD license.
## @see: https://github.com/mitsuhiko/python-pbkdf2/blob/master/LICENSE
##
import sys
PY3 = sys.version_info >= (3,)


import hmac
import hashlib
import random
from struct import Struct
from operator import xor

if PY3:
   izip = zip
else:
   from itertools import izip, starmap

_pack_int = Struct('>I').pack


def _pbkdf2_bin(data, salt, iterations = 1000, keylen = 32, hashfunc = None):
   hashfunc = hashfunc or hashlib.sha256
   mac = hmac.new(data, None, hashfunc)
   def _pseudorandom(x, mac=mac):
      h = mac.copy()
      h.update(x)
      return map(ord, h.digest())
   buf = []
   for block in xrange(1, -(-keylen // mac.digest_size) + 1):
      rv = u = _pseudorandom(salt + _pack_int(block))
      for i in xrange(iterations - 1):
         u = _pseudorandom(''.join(map(chr, u)))
         rv = starmap(xor, izip(rv, u))
      buf.extend(rv)
   return ''.join(map(chr, buf))[:keylen]



def derive_key(secret, salt, iterations = 1000, keylen = 32):
   """
   Computes a derived cryptographic key from a password according to PBKDF2.
   
   .. seealso:: http://en.wikipedia.org/wiki/PBKDF2

   :param secret: The secret.
   :type secret: bytes
   :param salt: The salt to be used.
   :type salt: bytes
   :param iterations: Number of iterations of derivation algorithm to run.
   :type iterations: int
   :param keylen: Length of the key to derive in bits.
   :type keylen: int

   :return: The derived key in Base64 encoding.
   :rtype: bytes
   """
   assert(type(secret) == bytes)
   assert(type(salt) == bytes)
   assert(type(iterations) in six.integer_types)
   assert(type(keylen) in six.integer_types)
   key = _pbkdf2_bin(secret, salt, iterations, keylen)
   return binascii.b2a_base64(key).strip()



WCS_SECRET_CHARSET = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
"""
The characters from which :func:`autobahn.wamp.auth.generate_wcs` generates secrets.
"""

def generate_wcs(length = 12):
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
   return b"".join([random.choice(WCS_SECRET_CHARSET) for _ in range(length)])



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
   assert(type(key) == bytes)
   assert(type(challenge) == bytes)
   sig = hmac.new(key, challenge, hashlib.sha256).digest()
   return binascii.b2a_base64(sig).strip()
