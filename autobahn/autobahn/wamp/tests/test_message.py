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

#import autobahn
from autobahn import wamp
#from autobahn.wamp import error
from autobahn.wamp.uri import Pattern
from autobahn.wamp import message


class KwException(Exception):
   def __init__(self, *args, **kwargs):
      Exception.__init__(self, *args)
      self.kwargs = kwargs


class MockSession:

   def __init__(self):
      self._ecls_to_uri_pat = {}
      self._uri_to_ecls = {}


   def define(self, exception, error = None):
      """
      Defines an exception for a WAMP error in the context of this WAMP session.
      """
      if error is None:
         assert(hasattr(exception, '_wampuris'))
         self._ecls_to_uri_pat[exception] = exception._wampuris
         self._uri_to_ecls[exception._wampuris[0].uri()] = exception
      else:
         assert(not hasattr(exception, '_wampuris'))
         self._ecls_to_uri_pat[exception] = [Pattern(error, Pattern.URI_TARGET_HANDLER)]
         self._uri_to_ecls[error] = exception


   def message_from_exception(self, request, exc):
      """
      Create a WAMP error message from an exception.

      :param request: The request ID this WAMP error message is for.
      :type request: int
      :param exc: The exception.
      :type exc: Instance of :class:`Exception` or subclass thereof.
      """
      if isinstance(exc, KwException):
         msg = message.Error(request, exc.args[0], args = exc.args[1:], kwargs = exc.kwargs)
      else:
         if self._ecls_to_uri_pat.has_key(exc.__class__):
            error = self._ecls_to_uri_pat[exc.__class__][0]._uri
         else:
            error = "wamp.error.runtime_error"

         if hasattr(exc, 'args'):
            if hasattr(exc, 'kwargs'):
               msg = message.Error(request, error, args = exc.args, kwargs = exc.kwargs)
            else:
               msg = message.Error(request, error, args = exc.args)
         else:
            msg = message.Error(request, error)

      return msg


   def exception_from_message(self, msg):
      """
      Create a user (or generic) exception from a WAMP error message.

      :param msg: A WAMP error message.
      :type msg: Instance of :class:`autobahn.wamp.message.Error`
      """

      # FIXME:
      # 1. map to ecls based on error URI wildcard/prefix
      # 2. extract additional args/kwargs from error URI

      exc = None

      if self._uri_to_ecls.has_key(msg.error):
         ecls = self._uri_to_ecls[msg.error]
         try:
            ## the following might fail, eg. TypeError when
            ## signature of exception constructor is incompatible
            ## with args/kwargs or when the exception constructor raises
            if msg.kwargs:
               if msg.args:
                  exc = ecls(*msg.args, **msg.kwargs)
               else:
                  exc = ecls(**msg.kwargs)
            else:
               if msg.args:
                  exc = ecls(*msg.args)
               else:
                  exc = ecls()
         except Exception as e:
            ## FIXME: log e
            pass

      if not exc:
         ## the following ctor never fails ..
         if msg.kwargs:
            if msg.args:
               exc = KwException(msg.error, *msg.args, **msg.kwargs)
            else:
               exc = KwException(msg.error, **msg.kwargs)
         else:
            if msg.args:
               exc = KwException(msg.error, *msg.args)
            else:
               exc = KwException(msg.error)

      return exc



class TestErrorMessage(unittest.TestCase):

   def test_exception_message_ctor(self):
      e = message.Error(123456, 'com.myapp.error1')
      msg = e.marshal()
      self.assertEqual(msg[0], message.Error.MESSAGE_TYPE)
      self.assertEqual(msg[1], 123456)
      self.assertEqual(msg[2], 'com.myapp.error1')
      self.assertEqual(msg[3], {})

      e = message.Error(123456, 'com.myapp.error1', args = [1, 2, 3], kwargs = {'foo': 23, 'bar': 'hello'})
      msg = e.marshal()
      self.assertEqual(msg[0], message.Error.MESSAGE_TYPE)
      self.assertEqual(msg[1], 123456)
      self.assertEqual(msg[2], 'com.myapp.error1')
      self.assertEqual(msg[3], {})
      self.assertEqual(msg[4], [1, 2, 3])
      self.assertEqual(msg[5], {'foo': 23, 'bar': 'hello'})


   def test_exception_parse(self):
      wmsg = [message.Error.MESSAGE_TYPE, 123456, 'com.myapp.error1', {}]
      msg = message.Error.parse(wmsg)
      self.assertEqual(msg.request, 123456)
      self.assertEqual(msg.error, 'com.myapp.error1')
      self.assertEqual(msg.args, None)
      self.assertEqual(msg.kwargs, None)

      wmsg = [message.Error.MESSAGE_TYPE, 123456, 'com.myapp.error1', {}, [1, 2, 3], {'foo': 23, 'bar': 'hello'}]
      msg = message.Error.parse(wmsg)
      self.assertEqual(msg.request, 123456)
      self.assertEqual(msg.error, 'com.myapp.error1')
      self.assertEqual(msg.args, [1, 2, 3])
      self.assertEqual(msg.kwargs, {'foo': 23, 'bar': 'hello'})


   def test_exception_from_message(self):
      session = MockSession()

      @wamp.error("com.myapp.error1")
      class AppError1(Exception):
         pass

      @wamp.error("com.myapp.error2")
      class AppError2(Exception):
         pass

      session.define(AppError1)
      session.define(AppError2)

      ## map defined errors to user exceptions
      ##
      emsg = message.Error(123456, 'com.myapp.error1')
      exc = session.exception_from_message(emsg)
      self.assertIsInstance(exc, AppError1)
      self.assertEqual(exc.args, ())

      emsg = message.Error(123456, 'com.myapp.error2')
      exc = session.exception_from_message(emsg)
      self.assertIsInstance(exc, AppError2)
      self.assertEqual(exc.args, ())

      ## map undefined error to (generic) exception
      ##
      emsg = message.Error(123456, 'com.myapp.error3')
      exc = session.exception_from_message(emsg)
      self.assertIsInstance(exc, KwException)
      self.assertEqual(exc.args, ('com.myapp.error3',))
      self.assertEqual(exc.kwargs, {})

      emsg = message.Error(123456, 'com.myapp.error3', args = [1, 2, 'hello'])
      exc = session.exception_from_message(emsg)
      self.assertIsInstance(exc, KwException)
      self.assertEqual(exc.args, ('com.myapp.error3', 1, 2, 'hello'))
      self.assertEqual(exc.kwargs, {})

      emsg = message.Error(123456, 'com.myapp.error3', args = [1, 2, 'hello'], kwargs = {'foo': 23, 'bar': 'baz'})
      exc = session.exception_from_message(emsg)
      self.assertIsInstance(exc, KwException)
      self.assertEqual(exc.args, ('com.myapp.error3', 1, 2, 'hello'))
      self.assertEqual(exc.kwargs, {'foo': 23, 'bar': 'baz'})
      

   def test_message_from_exception(self):
      session = MockSession()

      @wamp.error("com.myapp.error1")
      class AppError1(Exception):
         pass

      @wamp.error("com.myapp.error2")
      class AppError2(Exception):
         pass

      session.define(AppError1)
      session.define(AppError2)

      exc = AppError1()
      msg = session.message_from_exception(123456, exc)

      self.assertEqual(msg.marshal(), [message.Error.MESSAGE_TYPE, 123456, "com.myapp.error1", {}])


if __name__ == '__main__':
   unittest.main()
