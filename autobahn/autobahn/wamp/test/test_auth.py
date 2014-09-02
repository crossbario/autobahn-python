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

#from twisted.trial import unittest
import unittest

import re
import json

from autobahn.wamp.auth import generate_wcs, \
                               compute_wcs, \
                               derive_key, \
                               compute_totp, \
                               generate_totp_secret



class TestWampCra(unittest.TestCase):

   def test_generate_totp_secret_default(self):
      secret = generate_totp_secret()
      self.assertEqual(type(secret), bytes)
      self.assertEqual(len(secret), 10*8/5)


   def test_generate_totp_secret_length(self):
      for length in [5, 10, 20, 30, 40, 50]:
         secret = generate_totp_secret(length)
         self.assertEqual(type(secret), bytes)
         self.assertEqual(len(secret), length*8/5)


   def test_compute_totp(self):
      pat = re.compile(b"\d{6,6}")
      secret = b"MFRGGZDFMZTWQ2LK"
      signature = compute_totp(secret)
      self.assertEqual(type(signature), bytes)
      self.assertTrue(pat.match(signature) is not None)


   def test_compute_totp_offset(self):
      pat = re.compile(b"\d{6,6}")
      secret = b"MFRGGZDFMZTWQ2LK"
      for offset in range(-10, 10):
         signature = compute_totp(secret, offset)
         self.assertEqual(type(signature), bytes)
         self.assertTrue(pat.match(signature) is not None)


   def test_derive_key(self):
      secret = u'L3L1YUE8Txlw'
      salt = u'salt123'
      key = derive_key(secret.encode('utf8'), salt.encode('utf8'))
      self.assertEqual(type(key), bytes)
      self.assertEqual(key, b"qzcdsr9uu/L5hnss3kjNTRe490ETgA70ZBaB5rvnJ5Y=")


   def test_generate_wcs_default(self):
      secret = generate_wcs()
      self.assertEqual(type(secret), bytes)
      self.assertEqual(len(secret), 12)


   def test_generate_wcs_length(self):
      for length in [5, 10, 20, 30, 40, 50]:
         secret = generate_wcs(length)
         self.assertEqual(type(secret), bytes)
         self.assertEqual(len(secret), length)


   def test_compute_wcs(self):
      secret = u'L3L1YUE8Txlw'
      challenge = json.dumps([1,2,3], ensure_ascii = False).encode('utf8')
      signature = compute_wcs(secret.encode('utf8'), challenge)
      self.assertEqual(type(signature), bytes)
      self.assertEqual(signature, b"1njQtmmeYO41N5EWEzD2kAjjEKRZ5kPZt/TzpYXOzR0=")



if __name__ == '__main__':
   unittest.main()
