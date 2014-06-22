###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
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


import os
import base64
import hashlib
import hmac
import six
import struct
import time


def new_secret(short = False):
   """
   Generates a new base32 encoded, random secret.

   :param short: If `True`, generate 5 bytes entropy, else 10 bytes.
   :type short: bool

   :returns bytes -- The generated secret.
   """
   if short:
      return base64.b32encode(os.urandom(5))
   else:
      return base64.b32encode(os.urandom(10))


def compute_totp(secret, offset = 0):
   """
   Computes the current TOTP code.

   :param secret: Base32 encoded secret.
   :type secret: bytes
   :param offset: Time offset for which to compute TOTP.
   :type offset: int

   :retuns str -- TOTP for current time (+/- offset).
   """
   try:
      key = base64.b32decode(secret)
   except TypeError:
      raise Exception('invalid secret')
   interval = offset + int(time.time()) // 30
   msg = struct.pack('>Q', interval)
   digest = hmac.new(key, msg, hashlib.sha1).digest()
   o = 15 & (digest[19] if six.PY3 else ord(digest[19]))
   token = (struct.unpack('>I', digest[o:o+4])[0] & 0x7fffffff) % 1000000
   return six.b('{:06d}'.format(token))
