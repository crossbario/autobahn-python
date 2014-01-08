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

from autobahn import wamp2 as wamp
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



class TestDecorators(unittest.TestCase):

   def setUp(self):
      pass

   def tearDown(self):
      pass


   def test_decorate_endpoint(self):

      @wamp.procedure("com.calculator.square")
      def square(x):
         pass

      self.assertIsInstance(square._autobahn_uri, Pattern)
      self.assertTrue(square._autobahn_uri.is_endpoint())
      self.assertFalse(square._autobahn_uri.is_handler())
      self.assertEqual(square._autobahn_uri._type, Pattern.URI_TYPE_EXACT)

      @wamp.procedure("com.myapp.product.<int:product>.update")
      def update_product(product = None, label = None):
         pass

      self.assertIsInstance(update_product._autobahn_uri, Pattern)
      self.assertTrue(update_product._autobahn_uri.is_endpoint())
      self.assertFalse(update_product._autobahn_uri.is_handler())
      self.assertEqual(update_product._autobahn_uri._type, Pattern.URI_TYPE_WILDCARD)

      @wamp.procedure("com.myapp.<string:category>.<int:id>.update")
      def update(category = None, id = None):
         pass

      self.assertIsInstance(update._autobahn_uri, Pattern)
      self.assertTrue(update._autobahn_uri.is_endpoint())
      self.assertFalse(update._autobahn_uri.is_handler())
      self.assertEqual(update._autobahn_uri._type, Pattern.URI_TYPE_WILDCARD)


   def test_decorate_handler(self):

      @wamp.topic("com.myapp.on_shutdown")
      def on_shutdown():
         pass

      self.assertIsInstance(on_shutdown._autobahn_uri, Pattern)
      self.assertFalse(on_shutdown._autobahn_uri.is_endpoint())
      self.assertTrue(on_shutdown._autobahn_uri.is_handler())
      self.assertEqual(on_shutdown._autobahn_uri._type, Pattern.URI_TYPE_EXACT)

      @wamp.topic("com.myapp.product.<int:product>.on_update")
      def on_product_update(product = None, label = None):
         pass

      self.assertIsInstance(on_product_update._autobahn_uri, Pattern)
      self.assertFalse(on_product_update._autobahn_uri.is_endpoint())
      self.assertTrue(on_product_update._autobahn_uri.is_handler())
      self.assertEqual(on_product_update._autobahn_uri._type, Pattern.URI_TYPE_WILDCARD)

      @wamp.topic("com.myapp.<string:category>.<int:id>.on_update")
      def on_update(category = None, id = None, label = None):
         pass

      self.assertIsInstance(on_update._autobahn_uri, Pattern)
      self.assertFalse(on_update._autobahn_uri.is_endpoint())
      self.assertTrue(on_update._autobahn_uri.is_handler())
      self.assertEqual(on_update._autobahn_uri._type, Pattern.URI_TYPE_WILDCARD)


   def test_match_decorated_endpoint(self):

      @wamp.procedure("com.calculator.square")
      def square(x):
         return x

      kwargs = square._autobahn_uri.match("com.calculator.square")
      self.assertEqual(square(666, **kwargs), 666)

      @wamp.procedure("com.myapp.product.<int:product>.update")
      def update_product(product = None, label = None):
         return product, label

      kwargs = update_product._autobahn_uri.match("com.myapp.product.123456.update")
      kwargs['label'] = "foobar"
      self.assertEqual(update_product(**kwargs), (123456, "foobar"))

      @wamp.procedure("com.myapp.<string:category>.<int:id>.update")
      def update(category = None, id = None, label = None):
         return category, id, label

      kwargs = update._autobahn_uri.match("com.myapp.product.123456.update")
      kwargs['label'] = "foobar"
      self.assertEqual(update(**kwargs), ("product", 123456, "foobar"))


   def test_match_decorated_handler(self):

      @wamp.topic("com.myapp.on_shutdown")
      def on_shutdown():
         pass

      kwargs = on_shutdown._autobahn_uri.match("com.myapp.on_shutdown")
      self.assertEqual(on_shutdown(**kwargs), None)

      @wamp.topic("com.myapp.product.<int:product>.on_update")
      def on_product_update(product = None, label = None):
         return product, label

      kwargs = on_product_update._autobahn_uri.match("com.myapp.product.123456.on_update")
      kwargs['label'] = "foobar"
      self.assertEqual(on_product_update(**kwargs), (123456, "foobar"))

      @wamp.topic("com.myapp.<string:category>.<int:id>.on_update")
      def on_update(category = None, id = None, label = None):
         return category, id, label

      kwargs = on_update._autobahn_uri.match("com.myapp.product.123456.on_update")
      kwargs['label'] = "foobar"
      self.assertEqual(on_update(**kwargs), ("product", 123456, "foobar"))


if __name__ == '__main__':
   unittest.main()
