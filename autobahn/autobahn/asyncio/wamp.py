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

__all__ = (
   'FutureMixin',
   'ApplicationSession',
   'ApplicationSessionFactory',
   'ApplicationRunner'
)

try:
   import asyncio
   from asyncio import iscoroutine
   from asyncio import Future
except ImportError:
   ## Trollius >= 0.3 was renamed
   # noinspection PyUnresolvedReferences
   import trollius as asyncio
   from trollius import iscoroutine
   from trollius import Future

from autobahn.wamp import protocol
from autobahn.wamp.types import ComponentConfig
from autobahn.websocket.protocol import parseWsUrl
from autobahn.asyncio.websocket import WampWebSocketClientFactory



class FutureMixin:
   """
   Mixin for Asyncio style Futures.
   """

   @staticmethod
   def _create_future():
      return Future()

   @staticmethod
   def _as_future(fun, *args, **kwargs):
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

   @staticmethod
   def _resolve_future(future, value):
      future.set_result(value)

   @staticmethod
   def _reject_future(future, value):
      future.set_exception(value)

   @staticmethod
   def _add_future_callbacks(future, callback, errback):
      def done(f):
         try:
            res = f.result()
            callback(res)
         except Exception as e:
            errback(e)
      return future.add_done_callback(done)

   @staticmethod
   def _gather_futures(futures, consume_exceptions = True):
      return asyncio.gather(*futures, return_exceptions = consume_exceptions)

   def _call_later(self, delay, callback, *args, **kwargs):
      if self._loop:
         loop = self._loop
      else:
         loop = asyncio.get_event_loop()

      f = Future()

      def wrapper():
         try:
            result = callback(*args, **kwargs)
            f.set_result(result)
         except Exception as e:
            f.set_exception(e)

      return (loop.call_later(delay, wrapper), f)


class ApplicationSession(FutureMixin, protocol.ApplicationSession):
   """
   WAMP application session for asyncio-based applications.
   """



class ApplicationSessionFactory(FutureMixin, protocol.ApplicationSessionFactory):
   """
   WAMP application session factory for asyncio-based applications.
   """

   session = ApplicationSession
   """
   The application session class this application session factory will use. Defaults to :class:`autobahn.asyncio.wamp.ApplicationSession`.
   """



class ApplicationRunner:
   """
   This class is a convenience tool mainly for development and quick hosting
   of WAMP application components.

   It can host a WAMP application component in a WAMP-over-WebSocket client
   connecting to a WAMP router.
   """

   def __init__(self, url, realm, extra = None, serializers = None,
      debug = False, debug_wamp = False, debug_app = False):
      """

      :param url: The WebSocket URL of the WAMP router to connect to (e.g. `ws://somehost.com:8090/somepath`)
      :type url: unicode
      :param realm: The WAMP realm to join the application session to.
      :type realm: unicode
      :param extra: Optional extra configuration to forward to the application component.
      :type extra: dict
      :param serializers: A list of WAMP serializers to use (or None for default serializers).
         Serializers must implement :class:`autobahn.wamp.interfaces.ISerializer`.
      :type serializers: list
      :param debug: Turn on low-level debugging.
      :type debug: bool
      :param debug_wamp: Turn on WAMP-level debugging.
      :type debug_wamp: bool
      :param debug_app: Turn on app-level debugging.
      :type debug_app: bool
      """
      self.url = url
      self.realm = realm
      self.extra = extra or dict()
      self.debug = debug
      self.debug_wamp = debug_wamp
      self.debug_app = debug_app
      self.make = None
      self.serializers = serializers


   def run(self, make):
      """
      Run the application component.

      :param make: A factory that produces instances of :class:`autobahn.asyncio.wamp.ApplicationSession`
         when called with an instance of :class:`autobahn.wamp.types.ComponentConfig`.
      :type make: callable
      """
      ## 1) factory for use ApplicationSession
      def create():
         cfg = ComponentConfig(self.realm, self.extra)
         try:
            session = make(cfg)
         except Exception as e:
            ## the app component could not be created .. fatal
            print(e)
            asyncio.get_event_loop().stop()
         else:
            session.debug_app = self.debug_app
            return session

      isSecure, host, port, resource, path, params = parseWsUrl(self.url)

      ## 2) create a WAMP-over-WebSocket transport client factory
      transport_factory = WampWebSocketClientFactory(create, url = self.url, serializers = self.serializers,
         debug = self.debug, debug_wamp = self.debug_wamp)

      ## 3) start the client
      loop = asyncio.get_event_loop()
      coro = loop.create_connection(transport_factory, host, port, ssl = isSecure)
      loop.run_until_complete(coro)

      ## 4) now enter the asyncio event loop
      loop.run_forever()
      loop.close()
