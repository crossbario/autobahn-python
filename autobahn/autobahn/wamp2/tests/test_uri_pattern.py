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
                "com.myapp.<product:foo>.update",
                "com.myapp.<123:int>.update",
                "com.myapp.<:product>.update",
                "com.myapp.<product:>.update",
                "com.myapp.<int:>.update",
                ]:
         self.assertRaises(Exception, Pattern, u, Pattern.URI_TARGET_ENDPOINT)

   def test_valid_uris(self):
      for u in ["com.myapp.proc1",
                "com.myapp.<product:int>.update",
                ]:
         p = Pattern(u, Pattern.URI_TARGET_ENDPOINT)
         self.assertIsInstance(p, Pattern)

   def test_parse_uris(self):
      tests = [
         ("com.myapp.<product:int>.update", [
            ("com.myapp.0.update", {'product': 0}),
            ("com.myapp.123456.update", {'product': 123456}),
            ("com.myapp.aaa.update", None),
            ("com.myapp..update", None),
            ("com.myapp.0.delete", None),
            ]
         ),
         ("com.myapp.<product:string>.update", [
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
               args_is, kwargs_is = pat.match(uri)
               self.assertEqual(kwargs_is, kwargs_should)
            else:
               self.assertRaises(Exception, pat.match, uri)



class TestDecorators(unittest.TestCase):

   def test_decorate_endpoint(self):

      @wamp.procedure("com.calculator.square")
      def square(x):
         pass

      self.assertIsInstance(square._wampuri, Pattern)
      self.assertTrue(square._wampuri.is_endpoint())
      self.assertFalse(square._wampuri.is_handler())
      self.assertFalse(square._wampuri.is_exception())
      self.assertEqual(square._wampuri.uri(), "com.calculator.square")
      self.assertEqual(square._wampuri._type, Pattern.URI_TYPE_EXACT)

      @wamp.procedure("com.myapp.product.<product:int>.update")
      def update_product(product = None, label = None):
         pass

      self.assertIsInstance(update_product._wampuri, Pattern)
      self.assertTrue(update_product._wampuri.is_endpoint())
      self.assertFalse(update_product._wampuri.is_handler())
      self.assertFalse(update_product._wampuri.is_exception())
      self.assertEqual(update_product._wampuri.uri(), "com.myapp.product.<product:int>.update")
      self.assertEqual(update_product._wampuri._type, Pattern.URI_TYPE_WILDCARD)

      @wamp.procedure("com.myapp.<category:string>.<id:int>.update")
      def update(category = None, id = None):
         pass

      self.assertIsInstance(update._wampuri, Pattern)
      self.assertTrue(update._wampuri.is_endpoint())
      self.assertFalse(update._wampuri.is_handler())
      self.assertFalse(update._wampuri.is_exception())
      self.assertEqual(update._wampuri.uri(), "com.myapp.<category:string>.<id:int>.update")
      self.assertEqual(update._wampuri._type, Pattern.URI_TYPE_WILDCARD)


   def test_decorate_handler(self):

      @wamp.topic("com.myapp.on_shutdown")
      def on_shutdown():
         pass

      self.assertIsInstance(on_shutdown._wampuri, Pattern)
      self.assertFalse(on_shutdown._wampuri.is_endpoint())
      self.assertTrue(on_shutdown._wampuri.is_handler())
      self.assertFalse(on_shutdown._wampuri.is_exception())
      self.assertEqual(on_shutdown._wampuri.uri(), "com.myapp.on_shutdown")
      self.assertEqual(on_shutdown._wampuri._type, Pattern.URI_TYPE_EXACT)

      @wamp.topic("com.myapp.product.<product:int>.on_update")
      def on_product_update(product = None, label = None):
         pass

      self.assertIsInstance(on_product_update._wampuri, Pattern)
      self.assertFalse(on_product_update._wampuri.is_endpoint())
      self.assertTrue(on_product_update._wampuri.is_handler())
      self.assertFalse(on_product_update._wampuri.is_exception())
      self.assertEqual(on_product_update._wampuri.uri(), "com.myapp.product.<product:int>.on_update")
      self.assertEqual(on_product_update._wampuri._type, Pattern.URI_TYPE_WILDCARD)

      @wamp.topic("com.myapp.<category:string>.<id:int>.on_update")
      def on_update(category = None, id = None, label = None):
         pass

      self.assertIsInstance(on_update._wampuri, Pattern)
      self.assertFalse(on_update._wampuri.is_endpoint())
      self.assertTrue(on_update._wampuri.is_handler())
      self.assertFalse(on_update._wampuri.is_exception())
      self.assertEqual(on_update._wampuri.uri(), "com.myapp.<category:string>.<id:int>.on_update")
      self.assertEqual(on_update._wampuri._type, Pattern.URI_TYPE_WILDCARD)


   def test_decorate_exception(self):

      @wamp.error("com.myapp.error")
      class AppError(Exception):
         pass

      self.assertIsInstance(AppError._wampuri, Pattern)
      self.assertFalse(AppError._wampuri.is_endpoint())
      self.assertFalse(AppError._wampuri.is_handler())
      self.assertTrue(AppError._wampuri.is_exception())
      self.assertEqual(AppError._wampuri.uri(), "com.myapp.error")
      self.assertEqual(AppError._wampuri._type, Pattern.URI_TYPE_EXACT)

      @wamp.error("com.myapp.product.<product:int>.product_inactive")
      class ProductInactiveError(Exception):
         pass

      self.assertIsInstance(ProductInactiveError._wampuri, Pattern)
      self.assertFalse(ProductInactiveError._wampuri.is_endpoint())
      self.assertFalse(ProductInactiveError._wampuri.is_handler())
      self.assertTrue(ProductInactiveError._wampuri.is_exception())
      self.assertEqual(ProductInactiveError._wampuri.uri(), "com.myapp.product.<product:int>.product_inactive")
      self.assertEqual(ProductInactiveError._wampuri._type, Pattern.URI_TYPE_WILDCARD)

      @wamp.error("com.myapp.<category:string>.<product:int>.inactive")
      class ObjectInactiveError(Exception):
         pass

      self.assertIsInstance(ObjectInactiveError._wampuri, Pattern)
      self.assertFalse(ObjectInactiveError._wampuri.is_endpoint())
      self.assertFalse(ObjectInactiveError._wampuri.is_handler())
      self.assertTrue(ObjectInactiveError._wampuri.is_exception())
      self.assertEqual(ObjectInactiveError._wampuri.uri(), "com.myapp.<category:string>.<product:int>.inactive")
      self.assertEqual(ObjectInactiveError._wampuri._type, Pattern.URI_TYPE_WILDCARD)


   def test_match_decorated_endpoint(self):

      @wamp.procedure("com.calculator.square")
      def square(x):
         return x

      args, kwargs = square._wampuri.match("com.calculator.square")
      self.assertEqual(square(666, **kwargs), 666)

      @wamp.procedure("com.myapp.product.<product:int>.update")
      def update_product(product = None, label = None):
         return product, label

      args, kwargs = update_product._wampuri.match("com.myapp.product.123456.update")
      kwargs['label'] = "foobar"
      self.assertEqual(update_product(**kwargs), (123456, "foobar"))

      @wamp.procedure("com.myapp.<category:string>.<id:int>.update")
      def update(category = None, id = None, label = None):
         return category, id, label

      args, kwargs = update._wampuri.match("com.myapp.product.123456.update")
      kwargs['label'] = "foobar"
      self.assertEqual(update(**kwargs), ("product", 123456, "foobar"))


   def test_match_decorated_handler(self):

      @wamp.topic("com.myapp.on_shutdown")
      def on_shutdown():
         pass

      args, kwargs = on_shutdown._wampuri.match("com.myapp.on_shutdown")
      self.assertEqual(on_shutdown(**kwargs), None)

      @wamp.topic("com.myapp.product.<product:int>.on_update")
      def on_product_update(product = None, label = None):
         return product, label

      args, kwargs = on_product_update._wampuri.match("com.myapp.product.123456.on_update")
      kwargs['label'] = "foobar"
      self.assertEqual(on_product_update(**kwargs), (123456, "foobar"))

      @wamp.topic("com.myapp.<category:string>.<id:int>.on_update")
      def on_update(category = None, id = None, label = None):
         return category, id, label

      args, kwargs = on_update._wampuri.match("com.myapp.product.123456.on_update")
      kwargs['label'] = "foobar"
      self.assertEqual(on_update(**kwargs), ("product", 123456, "foobar"))


   def test_match_decorated_exception(self):

      @wamp.error("com.myapp.error")
      class AppError(Exception):

         def __init__(self, msg):
            Exception.__init__(self, msg)

         def __eq__(self, other):
            return self.__class__ == other.__class__ and \
                   self.args == other.args

      args, kwargs = AppError._wampuri.match("com.myapp.error")
      self.assertEqual(AppError("fuck", **kwargs), AppError("fuck"))


      @wamp.error("com.myapp.product.<product:int>.product_inactive")
      class ProductInactiveError(Exception):

         def __init__(self, msg, product = None):
            Exception.__init__(self, msg)
            self.product = product

         def __eq__(self, other):
            return self.__class__ == other.__class__ and \
                   self.args == other.args and \
                   self.product == other.product

      args, kwargs = ProductInactiveError._wampuri.match("com.myapp.product.123456.product_inactive")
      self.assertEqual(ProductInactiveError("fuck", **kwargs), ProductInactiveError("fuck", 123456))


      @wamp.error("com.myapp.<category:string>.<product:int>.inactive")
      class ObjectInactiveError(Exception):

         def __init__(self, msg, category = None, product = None):
            Exception.__init__(self, msg)
            self.category = category
            self.product = product

         def __eq__(self, other):
            return self.__class__ == other.__class__ and \
                   self.args == other.args and \
                   self.category == other.category and \
                   self.product == other.product

      args, kwargs = ObjectInactiveError._wampuri.match("com.myapp.product.123456.inactive")
      self.assertEqual(ObjectInactiveError("fuck", **kwargs), ObjectInactiveError("fuck", "product", 123456))


if __name__ == '__main__':
   unittest.main()
