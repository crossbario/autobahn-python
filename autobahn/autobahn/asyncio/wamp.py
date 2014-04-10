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

__all__ = ['ApplicationSession',
           'ApplicationSessionFactory',
           'RouterSession',
           'RouterSessionFactory']

from autobahn.wamp import protocol

import asyncio
from asyncio.tasks import iscoroutine
from asyncio import Future



class FutureMixin:
   """
   Mixin for Asyncio style Futures.
   """

   def _create_future(self):
      print("FutureMixin._create_future")
      return Future()

   def _as_future2(self, fun, *args, **kwargs):
      print("FutureMixin._as_future")
      try:
         res = fun(*args, **kwargs)
      except Exception as e:
         f = Future()
         f.set_exception(e)
         return f
      else:
         if isinstance(res, Future) or iscoroutine(res):
            return res
         else:
            f = Future()
            f.set_result(res)
            return f

   def _as_future(self, fun, *args, **kwargs):
      print("FutureMixin._as_future")
      try:
         res = fun(*args, **kwargs)
      except Exception as e:
         f = Future()
         f.set_exception(e)
         return f
      else:
         if isinstance(res, Future):
            return res
         elif iscoroutine(res):
            return asyncio.Task(res)
         else:
            f = Future()
            f.set_result(res)
            return f

   def _resolve_future(self, future, value):
      print("FutureMixin._resolve_future")
      future.set_result(value)

   def _reject_future(self, future, value):
      print("FutureMixin._reject_future")
      future.set_exception(value)

   def _add_future_callbacks(self, future, callback, errback):
      print("FutureMixin._add_future_callbacks")
      def done(f):
         try:
            res = f.result()
            callback(res)
         except Exception as e:
            errback(e)
      return future.add_done_callback(done)

   def _gather_futures(self, futures, consume_exceptions = True):
      print("FutureMixin._gather_futures")
      return asyncio.gather(futures, return_exception = consume_exceptions)      



class ApplicationSession(FutureMixin, protocol.ApplicationSession):
   """
   WAMP application session for asyncio-based applications.
   """


class ApplicationSessionFactory(FutureMixin, protocol.ApplicationSessionFactory):
   """
   WAMP application session factory for asyncio-based applications.
   """


class RouterSession(FutureMixin, protocol.RouterSession):
   """
   WAMP router session for asyncio-based applications.
   """


class RouterSessionFactory(FutureMixin, protocol.RouterSessionFactory):
   """
   WAMP router session factory for asyncio-based applications.
   """
   session = RouterSession
