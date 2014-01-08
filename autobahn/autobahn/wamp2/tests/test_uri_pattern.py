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

      self.assertTrue(hasattr(square, '_wampuris'))
      self.assertTrue(type(square._wampuris) == list)
      self.assertEqual(len(square._wampuris), 1)
      self.assertIsInstance(square._wampuris[0], Pattern)
      self.assertTrue(square._wampuris[0].is_endpoint())
      self.assertFalse(square._wampuris[0].is_handler())
      self.assertFalse(square._wampuris[0].is_exception())
      self.assertEqual(square._wampuris[0].uri(), "com.calculator.square")
      self.assertEqual(square._wampuris[0]._type, Pattern.URI_TYPE_EXACT)

      @wamp.procedure("com.myapp.product.<product:int>.update")
      def update_product(product = None, label = None):
         pass

      self.assertTrue(hasattr(update_product, '_wampuris'))
      self.assertTrue(type(update_product._wampuris) == list)
      self.assertEqual(len(update_product._wampuris), 1)
      self.assertIsInstance(update_product._wampuris[0], Pattern)
      self.assertTrue(update_product._wampuris[0].is_endpoint())
      self.assertFalse(update_product._wampuris[0].is_handler())
      self.assertFalse(update_product._wampuris[0].is_exception())
      self.assertEqual(update_product._wampuris[0].uri(), "com.myapp.product.<product:int>.update")
      self.assertEqual(update_product._wampuris[0]._type, Pattern.URI_TYPE_WILDCARD)

      @wamp.procedure("com.myapp.<category:string>.<id:int>.update")
      def update(category = None, id = None):
         pass

      self.assertTrue(hasattr(update, '_wampuris'))
      self.assertTrue(type(update._wampuris) == list)
      self.assertEqual(len(update._wampuris), 1)
      self.assertIsInstance(update._wampuris[0], Pattern)
      self.assertTrue(update._wampuris[0].is_endpoint())
      self.assertFalse(update._wampuris[0].is_handler())
      self.assertFalse(update._wampuris[0].is_exception())
      self.assertEqual(update._wampuris[0].uri(), "com.myapp.<category:string>.<id:int>.update")
      self.assertEqual(update._wampuris[0]._type, Pattern.URI_TYPE_WILDCARD)


   def test_decorate_handler(self):

      @wamp.topic("com.myapp.on_shutdown")
      def on_shutdown():
         pass

      self.assertTrue(hasattr(on_shutdown, '_wampuris'))
      self.assertTrue(type(on_shutdown._wampuris) == list)
      self.assertEqual(len(on_shutdown._wampuris), 1)
      self.assertIsInstance(on_shutdown._wampuris[0], Pattern)
      self.assertFalse(on_shutdown._wampuris[0].is_endpoint())
      self.assertTrue(on_shutdown._wampuris[0].is_handler())
      self.assertFalse(on_shutdown._wampuris[0].is_exception())
      self.assertEqual(on_shutdown._wampuris[0].uri(), "com.myapp.on_shutdown")
      self.assertEqual(on_shutdown._wampuris[0]._type, Pattern.URI_TYPE_EXACT)

      @wamp.topic("com.myapp.product.<product:int>.on_update")
      def on_product_update(product = None, label = None):
         pass

      self.assertTrue(hasattr(on_product_update, '_wampuris'))
      self.assertTrue(type(on_product_update._wampuris) == list)
      self.assertEqual(len(on_product_update._wampuris), 1)
      self.assertIsInstance(on_product_update._wampuris[0], Pattern)
      self.assertFalse(on_product_update._wampuris[0].is_endpoint())
      self.assertTrue(on_product_update._wampuris[0].is_handler())
      self.assertFalse(on_product_update._wampuris[0].is_exception())
      self.assertEqual(on_product_update._wampuris[0].uri(), "com.myapp.product.<product:int>.on_update")
      self.assertEqual(on_product_update._wampuris[0]._type, Pattern.URI_TYPE_WILDCARD)

      @wamp.topic("com.myapp.<category:string>.<id:int>.on_update")
      def on_update(category = None, id = None, label = None):
         pass

      self.assertTrue(hasattr(on_update, '_wampuris'))
      self.assertTrue(type(on_update._wampuris) == list)
      self.assertEqual(len(on_update._wampuris), 1)
      self.assertIsInstance(on_update._wampuris[0], Pattern)
      self.assertFalse(on_update._wampuris[0].is_endpoint())
      self.assertTrue(on_update._wampuris[0].is_handler())
      self.assertFalse(on_update._wampuris[0].is_exception())
      self.assertEqual(on_update._wampuris[0].uri(), "com.myapp.<category:string>.<id:int>.on_update")
      self.assertEqual(on_update._wampuris[0]._type, Pattern.URI_TYPE_WILDCARD)


   def test_decorate_exception(self):

      @wamp.error("com.myapp.error")
      class AppError(Exception):
         pass

      self.assertTrue(hasattr(AppError, '_wampuris'))
      self.assertTrue(type(AppError._wampuris) == list)
      self.assertEqual(len(AppError._wampuris), 1)
      self.assertIsInstance(AppError._wampuris[0], Pattern)
      self.assertFalse(AppError._wampuris[0].is_endpoint())
      self.assertFalse(AppError._wampuris[0].is_handler())
      self.assertTrue(AppError._wampuris[0].is_exception())
      self.assertEqual(AppError._wampuris[0].uri(), "com.myapp.error")
      self.assertEqual(AppError._wampuris[0]._type, Pattern.URI_TYPE_EXACT)

      @wamp.error("com.myapp.product.<product:int>.product_inactive")
      class ProductInactiveError(Exception):
         pass

      self.assertTrue(hasattr(ProductInactiveError, '_wampuris'))
      self.assertTrue(type(ProductInactiveError._wampuris) == list)
      self.assertEqual(len(ProductInactiveError._wampuris), 1)
      self.assertIsInstance(ProductInactiveError._wampuris[0], Pattern)
      self.assertFalse(ProductInactiveError._wampuris[0].is_endpoint())
      self.assertFalse(ProductInactiveError._wampuris[0].is_handler())
      self.assertTrue(ProductInactiveError._wampuris[0].is_exception())
      self.assertEqual(ProductInactiveError._wampuris[0].uri(), "com.myapp.product.<product:int>.product_inactive")
      self.assertEqual(ProductInactiveError._wampuris[0]._type, Pattern.URI_TYPE_WILDCARD)

      @wamp.error("com.myapp.<category:string>.<product:int>.inactive")
      class ObjectInactiveError(Exception):
         pass

      self.assertTrue(hasattr(ObjectInactiveError, '_wampuris'))
      self.assertTrue(type(ObjectInactiveError._wampuris) == list)
      self.assertEqual(len(ObjectInactiveError._wampuris), 1)
      self.assertIsInstance(ObjectInactiveError._wampuris[0], Pattern)
      self.assertFalse(ObjectInactiveError._wampuris[0].is_endpoint())
      self.assertFalse(ObjectInactiveError._wampuris[0].is_handler())
      self.assertTrue(ObjectInactiveError._wampuris[0].is_exception())
      self.assertEqual(ObjectInactiveError._wampuris[0].uri(), "com.myapp.<category:string>.<product:int>.inactive")
      self.assertEqual(ObjectInactiveError._wampuris[0]._type, Pattern.URI_TYPE_WILDCARD)


   def test_match_decorated_endpoint(self):

      @wamp.procedure("com.calculator.square")
      def square(x):
         return x

      args, kwargs = square._wampuris[0].match("com.calculator.square")
      self.assertEqual(square(666, **kwargs), 666)

      @wamp.procedure("com.myapp.product.<product:int>.update")
      def update_product(product = None, label = None):
         return product, label

      args, kwargs = update_product._wampuris[0].match("com.myapp.product.123456.update")
      kwargs['label'] = "foobar"
      self.assertEqual(update_product(**kwargs), (123456, "foobar"))

      @wamp.procedure("com.myapp.<category:string>.<id:int>.update")
      def update(category = None, id = None, label = None):
         return category, id, label

      args, kwargs = update._wampuris[0].match("com.myapp.product.123456.update")
      kwargs['label'] = "foobar"
      self.assertEqual(update(**kwargs), ("product", 123456, "foobar"))


   def test_match_decorated_handler(self):

      @wamp.topic("com.myapp.on_shutdown")
      def on_shutdown():
         pass

      args, kwargs = on_shutdown._wampuris[0].match("com.myapp.on_shutdown")
      self.assertEqual(on_shutdown(**kwargs), None)

      @wamp.topic("com.myapp.product.<product:int>.on_update")
      def on_product_update(product = None, label = None):
         return product, label

      args, kwargs = on_product_update._wampuris[0].match("com.myapp.product.123456.on_update")
      kwargs['label'] = "foobar"
      self.assertEqual(on_product_update(**kwargs), (123456, "foobar"))

      @wamp.topic("com.myapp.<category:string>.<id:int>.on_update")
      def on_update(category = None, id = None, label = None):
         return category, id, label

      args, kwargs = on_update._wampuris[0].match("com.myapp.product.123456.on_update")
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

      args, kwargs = AppError._wampuris[0].match("com.myapp.error")
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

      args, kwargs = ProductInactiveError._wampuris[0].match("com.myapp.product.123456.product_inactive")
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

      args, kwargs = ObjectInactiveError._wampuris[0].match("com.myapp.product.123456.inactive")
      self.assertEqual(ObjectInactiveError("fuck", **kwargs), ObjectInactiveError("fuck", "product", 123456))



class TestDecoratorsAdvanced(unittest.TestCase):

   def test_decorate_exception_non_exception(self):

      def test():
         @wamp.error("com.test.error")
         class Foo:
            pass

      self.assertRaises(Exception, test)


   def test_decorate_endpoint_multiple(self):

      @wamp.procedure("com.oldapp.oldproc")
      @wamp.procedure("com.calculator.square")
      def square(x):
         pass

      self.assertTrue(hasattr(square, '_wampuris'))
      self.assertTrue(type(square._wampuris) == list)
      self.assertEqual(len(square._wampuris), 2)

      for i in range(2):
         self.assertIsInstance(square._wampuris[i], Pattern)
         self.assertTrue(square._wampuris[i].is_endpoint())
         self.assertFalse(square._wampuris[i].is_handler())
         self.assertFalse(square._wampuris[i].is_exception())
         self.assertEqual(square._wampuris[i]._type, Pattern.URI_TYPE_EXACT)

      self.assertEqual(square._wampuris[0].uri(), "com.calculator.square")
      self.assertEqual(square._wampuris[1].uri(), "com.oldapp.oldproc")


if __name__ == '__main__':
   unittest.main()
