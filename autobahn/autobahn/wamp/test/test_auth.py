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

import json

from autobahn.wamp.auth import generate_wcs, \
                               compute_wcs


class TestWampCra(unittest.TestCase):

   def test_generate_wcs_default(self):
      secret = generate_wcs()
      self.assertEqual(type(secret), unicode)
      self.assertEqual(len(secret), 12)

   def test_generate_wcs_length(self):
      length = 30
      secret = generate_wcs(length)
      self.assertEqual(type(secret), unicode)
      self.assertEqual(len(secret), length)

   def test_compute_wcs(self):
      secret = u'L3L1YUE8Txlw'
      challenge = json.dumps([1,2,3])
      signature = compute_wcs(secret.encode('ascii'), challenge)
      self.assertEqual(signature, u"1njQtmmeYO41N5EWEzD2kAjjEKRZ5kPZt/TzpYXOzR0=")




if __name__ == '__main__':
   unittest.main()
