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

from twisted.trial import unittest
#import unittest

from autobahn.wamp2.uri import Pattern



class TestUris(unittest.TestCase):

   def setUp(self):
      pass

   def tearDown(self):
      pass

   def test_invalid_uris(self):
      for u in ["",
                "123",
                "com.myapp.<foo:product>.update",
                "com.myapp.<int:123>.update",
                "com.myapp.<:product>.update",
                "com.myapp.<int:>.update",
                ]:
         self.assertRaises(Exception, Pattern, u, Pattern.URI_TARGET_ENDPOINT)

   def test_valid_uris(self):
      for u in ["com.myapp.proc1",
                "com.myapp.<int:product>.update",
                ]:
         p = Pattern(u, Pattern.URI_TARGET_ENDPOINT)
         self.assertIsInstance(p, Pattern)

   def test_parse_uris(self):
      tests = [
         ("com.myapp.<int:product>.update", [
            ("com.myapp.0.update", {'product': 0}),
            ("com.myapp.123456.update", {'product': 123456}),
            ("com.myapp.aaa.update", None),
            ("com.myapp..update", None),
            ("com.myapp.0.delete", None),
            ]
         ),
         ("com.myapp.<string:product>.update", [
            ("com.myapp.box.update", {'product': 'box'}),
            ("com.myapp.123456.update", {'product': '123456'}),
            ("com.myapp..update", None),
            ]
         )
      ]
      for test in tests:
         pat = Pattern(test[0], Pattern.URI_TARGET_ENDPOINT)
         for ptest in test[1]:
            uri = ptest[0]
            kwargs_should = ptest[1]
            if kwargs_should is not None:
               kwargs_is = pat.match(uri)
               self.assertEqual(kwargs_is, kwargs_should)
            else:
               self.assertRaises(Exception, pat.match, uri)


if __name__ == '__main__':
   unittest.main()
