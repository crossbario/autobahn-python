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

from autobahn import wamp
from autobahn.wamp.uri import Pattern, RegisterOptions, SubscribeOptions

import unittest


class TestUris(unittest.TestCase):

    def test_invalid_uris(self):
        for u in ["",
                  "com.myapp.<product:foo>.update",
                  "com.myapp.<123:int>.update",
                  "com.myapp.<:product>.update",
                  "com.myapp.<product:>.update",
                  "com.myapp.<int:>.update",
                  ]:
            self.assertRaises(Exception, Pattern, u, Pattern.URI_TARGET_ENDPOINT)

    def test_valid_uris(self):
        for u in ["com.myapp.proc1",
                  "123",
                  "com.myapp.<product:int>.update",
                  "com.myapp.<category:string>.<subcategory>.list"
                  "com.myapp.something..update"
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
            ]),
            ("com.myapp.<product:string>.update", [
                ("com.myapp.box.update", {'product': 'box'}),
                ("com.myapp.123456.update", {'product': '123456'}),
                ("com.myapp..update", None),
            ]),
            ("com.myapp.<product>.update", [
                ("com.myapp.0.update", {'product': '0'}),
                ("com.myapp.abc.update", {'product': 'abc'}),
                ("com.myapp..update", None),
            ]),
            ("com.myapp.<category:string>.<subcategory:string>.list", [
                ("com.myapp.cosmetic.shampoo.list", {'category': 'cosmetic', 'subcategory': 'shampoo'}),
                ("com.myapp...list", None),
                ("com.myapp.cosmetic..list", None),
                ("com.myapp..shampoo.list", None),
            ]),
            ("eth.pydefi.tradeclock.<clock_oid:str>.get_clock_info", [
                ("eth.pydefi.tradeclock.ba3b1e9f-3006-4eae-ae88-cf5896b36342.get_clock_info",
                 {"clock_oid": "ba3b1e9f-3006-4eae-ae88-cf5896b36342"}),
            ]),
            ("eth.wamp.network.catalog.<catalog_adr:str>.owner", [
                ("eth.wamp.network.catalog.0xAA8Cc377db31a354137d8Bb86D0E38495dbD5266.owner",
                 {"catalog_adr": "0xAA8Cc377db31a354137d8Bb86D0E38495dbD5266"}),
            ]),
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
        @wamp.register("com.calculator.square")
        def square(_):
            """Do nothing."""

        self.assertTrue(hasattr(square, '_wampuris'))
        self.assertTrue(type(square._wampuris) == list)
        self.assertEqual(len(square._wampuris), 1)
        self.assertIsInstance(square._wampuris[0], Pattern)
        self.assertTrue(square._wampuris[0].is_endpoint())
        self.assertFalse(square._wampuris[0].is_handler())
        self.assertFalse(square._wampuris[0].is_exception())
        self.assertEqual(square._wampuris[0].uri(), "com.calculator.square")
        self.assertEqual(square._wampuris[0]._type, Pattern.URI_TYPE_EXACT)

        @wamp.register("com.myapp.product.<product:int>.update")
        def update_product(product=None, label=None):
            """Do nothing."""

        self.assertTrue(hasattr(update_product, '_wampuris'))
        self.assertTrue(type(update_product._wampuris) == list)
        self.assertEqual(len(update_product._wampuris), 1)
        self.assertIsInstance(update_product._wampuris[0], Pattern)
        self.assertTrue(update_product._wampuris[0].is_endpoint())
        self.assertFalse(update_product._wampuris[0].is_handler())
        self.assertFalse(update_product._wampuris[0].is_exception())
        self.assertEqual(update_product._wampuris[0].uri(), "com.myapp.product.<product:int>.update")
        self.assertEqual(update_product._wampuris[0]._type, Pattern.URI_TYPE_WILDCARD)

        @wamp.register("com.myapp.<category:string>.<cid:int>.update")
        def update(category=None, cid=None):
            """Do nothing."""

        self.assertTrue(hasattr(update, '_wampuris'))
        self.assertTrue(type(update._wampuris) == list)
        self.assertEqual(len(update._wampuris), 1)
        self.assertIsInstance(update._wampuris[0], Pattern)
        self.assertTrue(update._wampuris[0].is_endpoint())
        self.assertFalse(update._wampuris[0].is_handler())
        self.assertFalse(update._wampuris[0].is_exception())
        self.assertEqual(update._wampuris[0].uri(), "com.myapp.<category:string>.<cid:int>.update")
        self.assertEqual(update._wampuris[0]._type, Pattern.URI_TYPE_WILDCARD)

        @wamp.register("com.myapp.circle.<name:string>",
                       RegisterOptions(match="wildcard", details_arg="details"))
        def circle(name=None, details=None):
            """ Do nothing. """

        self.assertTrue(hasattr(circle, '_wampuris'))
        self.assertTrue(type(circle._wampuris) == list)
        self.assertEqual(len(circle._wampuris), 1)
        self.assertIsInstance(circle._wampuris[0], Pattern)
        self.assertIsInstance(circle._wampuris[0].options, RegisterOptions)
        self.assertEqual(circle._wampuris[0].options.match, "wildcard")
        self.assertEqual(circle._wampuris[0].options.details_arg, "details")
        self.assertTrue(circle._wampuris[0].is_endpoint())
        self.assertFalse(circle._wampuris[0].is_handler())
        self.assertFalse(circle._wampuris[0].is_exception())
        self.assertEqual(circle._wampuris[0].uri(), "com.myapp.circle.<name:string>")
        self.assertEqual(circle._wampuris[0]._type, Pattern.URI_TYPE_WILDCARD)

        @wamp.register("com.myapp.something..update",
                       RegisterOptions(match="wildcard", details_arg="details"))
        def something(dynamic=None, details=None):
            """ Do nothing. """

        self.assertTrue(hasattr(something, '_wampuris'))
        self.assertTrue(type(something._wampuris) == list)
        self.assertEqual(len(something._wampuris), 1)
        self.assertIsInstance(something._wampuris[0], Pattern)
        self.assertIsInstance(something._wampuris[0].options, RegisterOptions)
        self.assertEqual(something._wampuris[0].options.match, "wildcard")
        self.assertEqual(something._wampuris[0].options.details_arg, "details")
        self.assertTrue(something._wampuris[0].is_endpoint())
        self.assertFalse(something._wampuris[0].is_handler())
        self.assertFalse(something._wampuris[0].is_exception())
        self.assertEqual(something._wampuris[0].uri(), "com.myapp.something..update")
        self.assertEqual(something._wampuris[0]._type, Pattern.URI_TYPE_WILDCARD)

    def test_decorate_handler(self):
        @wamp.subscribe("com.myapp.on_shutdown")
        def on_shutdown():
            """Do nothing."""

        self.assertTrue(hasattr(on_shutdown, '_wampuris'))
        self.assertTrue(type(on_shutdown._wampuris) == list)
        self.assertEqual(len(on_shutdown._wampuris), 1)
        self.assertIsInstance(on_shutdown._wampuris[0], Pattern)
        self.assertFalse(on_shutdown._wampuris[0].is_endpoint())
        self.assertTrue(on_shutdown._wampuris[0].is_handler())
        self.assertFalse(on_shutdown._wampuris[0].is_exception())
        self.assertEqual(on_shutdown._wampuris[0].uri(), "com.myapp.on_shutdown")
        self.assertEqual(on_shutdown._wampuris[0]._type, Pattern.URI_TYPE_EXACT)

        @wamp.subscribe("com.myapp.product.<product:int>.on_update")
        def on_product_update(product=None, label=None):
            """Do nothing."""

        self.assertTrue(hasattr(on_product_update, '_wampuris'))
        self.assertTrue(type(on_product_update._wampuris) == list)
        self.assertEqual(len(on_product_update._wampuris), 1)
        self.assertIsInstance(on_product_update._wampuris[0], Pattern)
        self.assertFalse(on_product_update._wampuris[0].is_endpoint())
        self.assertTrue(on_product_update._wampuris[0].is_handler())
        self.assertFalse(on_product_update._wampuris[0].is_exception())
        self.assertEqual(on_product_update._wampuris[0].uri(), "com.myapp.product.<product:int>.on_update")
        self.assertEqual(on_product_update._wampuris[0]._type, Pattern.URI_TYPE_WILDCARD)

        @wamp.subscribe("com.myapp.<category:string>.<cid:int>.on_update")
        def on_update(category=None, cid=None, label=None):
            """Do nothing."""

        self.assertTrue(hasattr(on_update, '_wampuris'))
        self.assertTrue(type(on_update._wampuris) == list)
        self.assertEqual(len(on_update._wampuris), 1)
        self.assertIsInstance(on_update._wampuris[0], Pattern)
        self.assertFalse(on_update._wampuris[0].is_endpoint())
        self.assertTrue(on_update._wampuris[0].is_handler())
        self.assertFalse(on_update._wampuris[0].is_exception())
        self.assertEqual(on_update._wampuris[0].uri(), "com.myapp.<category:string>.<cid:int>.on_update")
        self.assertEqual(on_update._wampuris[0]._type, Pattern.URI_TYPE_WILDCARD)

        @wamp.subscribe("com.myapp.on.<event:string>",
                        SubscribeOptions(match="wildcard", details_arg="details"))
        def on_event(event=None, details=None):
            """ Do nothing. """

        self.assertTrue(hasattr(on_event, '_wampuris'))
        self.assertTrue(type(on_event._wampuris) == list)
        self.assertEqual(len(on_event._wampuris), 1)
        self.assertIsInstance(on_event._wampuris[0], Pattern)
        self.assertIsInstance(on_event._wampuris[0].options, SubscribeOptions)
        self.assertEqual(on_event._wampuris[0].options.match, "wildcard")
        self.assertEqual(on_event._wampuris[0].options.details_arg, "details")
        self.assertFalse(on_event._wampuris[0].is_endpoint())
        self.assertTrue(on_event._wampuris[0].is_handler())
        self.assertFalse(on_event._wampuris[0].is_exception())
        self.assertEqual(on_event._wampuris[0].uri(), "com.myapp.on.<event:string>")
        self.assertEqual(on_event._wampuris[0]._type, Pattern.URI_TYPE_WILDCARD)

    def test_decorate_exception(self):
        @wamp.error("com.myapp.error")
        class AppError(Exception):
            """Do nothing."""

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
            """Do nothing."""

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
            """Do nothing."""

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
        @wamp.register("com.calculator.square")
        def square(x):
            return x

        args, kwargs = square._wampuris[0].match("com.calculator.square")
        self.assertEqual(square(666, **kwargs), 666)

        @wamp.register("com.myapp.product.<product:int>.update")
        def update_product(product=None, label=None):
            return product, label

        args, kwargs = update_product._wampuris[0].match("com.myapp.product.123456.update")
        kwargs['label'] = "foobar"
        self.assertEqual(update_product(**kwargs), (123456, "foobar"))

        @wamp.register("com.myapp.<category:string>.<cid:int>.update")
        def update(category=None, cid=None, label=None):
            return category, cid, label

        args, kwargs = update._wampuris[0].match("com.myapp.product.123456.update")
        kwargs['label'] = "foobar"
        self.assertEqual(update(**kwargs), ("product", 123456, "foobar"))

    def test_match_decorated_handler(self):
        @wamp.subscribe("com.myapp.on_shutdown")
        def on_shutdown():
            pass

        args, kwargs = on_shutdown._wampuris[0].match("com.myapp.on_shutdown")
        self.assertEqual(on_shutdown(**kwargs), None)

        @wamp.subscribe("com.myapp.product.<product:int>.on_update")
        def on_product_update(product=None, label=None):
            return product, label

        args, kwargs = on_product_update._wampuris[0].match("com.myapp.product.123456.on_update")
        kwargs['label'] = "foobar"
        self.assertEqual(on_product_update(**kwargs), (123456, "foobar"))

        @wamp.subscribe("com.myapp.<category:string>.<cid:int>.on_update")
        def on_update(category=None, cid=None, label=None):
            return category, cid, label

        args, kwargs = on_update._wampuris[0].match("com.myapp.product.123456.on_update")
        kwargs['label'] = "foobar"
        self.assertEqual(on_update(**kwargs), ("product", 123456, "foobar"))

    def test_match_decorated_exception(self):
        @wamp.error("com.myapp.error")
        class AppError(Exception):

            def __init__(self, msg):
                Exception.__init__(self, msg)

            def __eq__(self, other):
                return self.__class__ == other.__class__ and self.args == other.args

        args, kwargs = AppError._wampuris[0].match("com.myapp.error")
        # noinspection PyArgumentList
        self.assertEqual(AppError("fuck", **kwargs), AppError("fuck"))

        @wamp.error("com.myapp.product.<product:int>.product_inactive")
        class ProductInactiveError(Exception):

            def __init__(self, msg, product=None):
                Exception.__init__(self, msg)
                self.product = product

            def __eq__(self, other):
                return self.__class__ == other.__class__ and self.args == other.args and self.product == other.product

        args, kwargs = ProductInactiveError._wampuris[0].match("com.myapp.product.123456.product_inactive")
        self.assertEqual(ProductInactiveError("fuck", **kwargs), ProductInactiveError("fuck", 123456))

        @wamp.error("com.myapp.<category:string>.<product:int>.inactive")
        class ObjectInactiveError(Exception):

            def __init__(self, msg, category=None, product=None):
                Exception.__init__(self, msg)
                self.category = category
                self.product = product

            def __eq__(self, other):
                return self.__class__ == other.__class__ and self.args == other.args and \
                    self.category == other.category and self.product == other.product

        args, kwargs = ObjectInactiveError._wampuris[0].match("com.myapp.product.123456.inactive")
        self.assertEqual(ObjectInactiveError("fuck", **kwargs), ObjectInactiveError("fuck", "product", 123456))


class KwException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)
        self.kwargs = kwargs


# what if the WAMP error message received
# contains args/kwargs that cannot be
# consumed by the constructor of the exception
# class defined for the WAMP error URI?

# 1. we can bail out (but we are already signaling an error)
# 2. we can require a generic constructor
# 3. we can map only unconsumed args/kwargs to generic attributes
# 4. we can silently drop unconsumed args/kwargs


class MockSession(object):

    def __init__(self):
        self._ecls_to_uri_pat = {}
        self._uri_to_ecls = {}

    def define(self, exception, error=None):
        if error is None:
            assert (hasattr(exception, '_wampuris'))
            self._ecls_to_uri_pat[exception] = exception._wampuris
            self._uri_to_ecls[exception._wampuris[0].uri()] = exception
        else:
            assert (not hasattr(exception, '_wampuris'))
            self._ecls_to_uri_pat[exception] = [Pattern(error, Pattern.URI_TARGET_HANDLER)]
            self._uri_to_ecls[error] = exception

    def map_error(self, error, args=None, kwargs=None):

        # FIXME:
        # 1. map to ecls based on error URI wildcard/prefix
        # 2. extract additional args/kwargs from error URI

        if error in self._uri_to_ecls:
            ecls = self._uri_to_ecls[error]
            try:
                # the following might fail, eg. TypeError when
                # signature of exception constructor is incompatible
                # with args/kwargs or when the exception constructor raises
                if kwargs:
                    if args:
                        exc = ecls(*args, **kwargs)
                    else:
                        exc = ecls(**kwargs)
                else:
                    if args:
                        exc = ecls(*args)
                    else:
                        exc = ecls()
            except Exception:
                # FIXME: log e
                exc = KwException(error, *args, **kwargs)
        else:
            # this never fails
            args = args or []
            kwargs = kwargs or {}
            exc = KwException(error, *args, **kwargs)
        return exc


class TestDecoratorsAdvanced(unittest.TestCase):

    def test_decorate_exception_non_exception(self):

        def test():
            # noinspection PyUnusedLocal
            @wamp.error("com.test.error")
            class Foo(object):
                pass

        self.assertRaises(Exception, test)

    def test_decorate_endpoint_multiple(self):

        # noinspection PyUnusedLocal
        @wamp.register("com.oldapp.oldproc")
        @wamp.register("com.calculator.square")
        def square(x):
            """Do nothing."""

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

    def test_marshal_decorated_exception(self):

        @wamp.error("com.myapp.error")
        class AppError(Exception):
            pass

        try:
            raise AppError("fuck")
        except Exception as e:
            self.assertEqual(e._wampuris[0].uri(), "com.myapp.error")

        @wamp.error("com.myapp.product.<product:int>.product_inactive")
        class ProductInactiveError(Exception):

            def __init__(self, msg, product=None):
                Exception.__init__(self, msg)
                self.product = product

        try:
            raise ProductInactiveError("fuck", 123456)
        except Exception as e:
            self.assertEqual(e._wampuris[0].uri(), "com.myapp.product.<product:int>.product_inactive")

        session = MockSession()
        session.define(AppError)

    def test_define_exception_undecorated(self):

        session = MockSession()

        class AppError(Exception):
            pass

        # defining an undecorated exception requires
        # an URI to be provided
        self.assertRaises(Exception, session.define, AppError)

        session.define(AppError, "com.myapp.error")

        exc = session.map_error("com.myapp.error")
        self.assertIsInstance(exc, AppError)

    def test_define_exception_decorated(self):

        session = MockSession()

        @wamp.error("com.myapp.error")
        class AppError(Exception):
            pass

        # when defining a decorated exception
        # an URI must not be provided
        self.assertRaises(Exception, session.define, AppError, "com.myapp.error")

        session.define(AppError)

        exc = session.map_error("com.myapp.error")
        self.assertIsInstance(exc, AppError)

    def test_map_exception_undefined(self):

        session = MockSession()

        exc = session.map_error("com.myapp.error")
        self.assertIsInstance(exc, Exception)

    def test_map_exception_args(self):

        session = MockSession()

        @wamp.error("com.myapp.error")
        class AppError(Exception):
            pass

        @wamp.error("com.myapp.error.product_inactive")
        class ProductInactiveError(Exception):
            def __init__(self, product=None):
                self.product = product

        # define exceptions in mock session
        session.define(AppError)
        session.define(ProductInactiveError)

        for test in [
            # ("com.myapp.foo.error", [], {}, KwException),
            ("com.myapp.error", [], {}, AppError),
            ("com.myapp.error", ["you are doing it wrong"], {}, AppError),
            ("com.myapp.error", ["you are doing it wrong", 1, 2, 3], {}, AppError),

            ("com.myapp.error.product_inactive", [], {}, ProductInactiveError),
            ("com.myapp.error.product_inactive", [], {"product": 123456}, ProductInactiveError),
        ]:
            error, args, kwargs, ecls = test
            exc = session.map_error(error, args, kwargs)

            self.assertIsInstance(exc, ecls)
            self.assertEqual(list(exc.args), args)
