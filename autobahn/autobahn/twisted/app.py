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

import inspect

from twisted.python import log
from twisted.internet.defer import inlineCallbacks

from autobahn.wamp import types
from autobahn.twisted.wamp import ApplicationSession, \
                                  ApplicationRunner



class _ApplicationSession(ApplicationSession):
   """
   WAMP application session class used internally with :class:`autobahn.twisted.app.Application`.
   """

   def __init__(self, config, app):
      """
      Ctor.

      :param config: The component configuration.
      :type config: Instance of :class:`autobahn.wamp.types.ComponentConfig`
      :param app: The application this session is for.
      :type app: Instance of :class:`autobahn.twisted.app.Application`.
      """
      ApplicationSession.__init__(self, config)
      self.app = app


   def onConnect(self):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.onConnect`
      """
      yield self.app._fire_signal('onconnect')
      self.join(self.config.realm)


   @inlineCallbacks
   def onJoin(self, details):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.onJoin`
      """
      for uri, proc in self.app._procs:
         yield self.register(proc, uri)

      for uri, handler in self.app._handlers:
         yield self.subscribe(handler, uri)

      yield self.app._fire_signal('onjoined')


   def onLeave(self, details):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.onLeave`
      """
      yield self.app._fire_signal('onleave')
      self.disconnect()


   def onDisconnect(self):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.onDisconnect`
      """
      yield self.app._fire_signal('ondisconnect')




class Application:
   """
   A WAMP application. The application object provides a simple way of
   creating, debugging and running WAMP application components.
   """

   def __init__(self, prefix = None):
      """
      Ctor.

      :param prefix: The application URI prefix to use for procedures and topics,
         e.g. `com.example.myapp`.
      :type prefix: str
      """
      self._prefix = prefix

      ## procedures to be registered once the app session has joined the router/realm
      self._procs = []

      ## event handler to be subscribed once the app session has joined the router/realm
      self._handlers = []

      ## app lifecycle signal handlers
      self._signals = {}

      ## once an app session is connected, this will be here
      self.session = None


   def __call__(self, config):
      """
      Factory creating a WAMP application session for the application.

      :param config: Component configuration.
      :type config: Instance of :class:`autobahn.wamp.types.ComponentConfig`

      :returns: obj -- An object that derives of
         :class:`autobahn.twisted.wamp.ApplicationSession`
      """
      assert(self.session is None)
      self.session = _ApplicationSession(config, self)
      return self.session


   def run(self, url = "ws://localhost:8080/ws", realm = "realm1", standalone = True):
      """
      Run the application.

      :param url: The URL of the WAMP router to connect to.
      :type url: str
      :param realm: The realm on the WAMP router to join.
      :type realm: str
      :param standalone: If `True`, run an embedded WAMP router instead of connecting
         to an external one. This is useful during development and debugging.
      """
      if standalone:
         print("Running on {} ..".format(url))
      runner = ApplicationRunner(url, realm, standalone = standalone)
      runner.run(self.__call__)


   def register(self, uri = None):
      """
      Decorator exposing a function as a remote callable procedure.

      The first argument of the decorator should be the URI of the procedure
      to register under.

      :Example:

      .. code-block:: python

         @app.register('com.myapp.add2')
         def add2(a, b):
            return a + b

      Above function can then be called remotely over WAMP using the URI `com.myapp.add2`
      the function was registered under.

      If no URI is given, the URI is constructed from the application URI prefix
      and the Python function name.

      :Example:

      .. code-block:: python

         app = Application('com.myapp')

         # implicit URI will be 'com.myapp.add2'
         @app.register()
         def add2(a, b):
            return a + b

      If the function `yields` (is a co-routine), the `@inlineCallbacks` decorator
      will be applied automatically to it. In that case, if you wish to return something,
      you should use `returnValue`:

      :Example:

      .. code-block:: python

         from twisted.internet.defer import returnValue

         @app.register('com.myapp.add2')
         def add2(a, b):
            res = yield stuff(a, b)
            returnValue(res)

      :param uri: The URI of the procedure to register under.
      :type uri: str
      """
      def decorator(func):
         if uri:
            _uri = uri
         else:
            assert(self._prefix is not None)
            _uri = "{}.{}".format(self._prefix, func.__name__)

         if inspect.isgeneratorfunction(func):
            func = inlineCallbacks(func)

         self._procs.append((_uri, func))
         return func
      return decorator


   def subscribe(self, uri = None):
      """
      Decorator attaching a function as an event handler.

      The first argument of the decorator should be the URI of the topic
      to subscribe to. If no URI is given, the URI is constructed from
      the application URI prefix and the Python function name.

      If the function yield, it will be assumed that it's an asychronous
      process and inlineCallbacks will be applied to it.

      :Example:

      .. code-block:: python

         @app.subscribe('com.myapp.topic1')
         def onevent1(x, y):
            print("got event on topic1", x, y)

      :param uri: The URI of the topic to subscribe to.
      :type uri: str
      """
      def decorator(func):
         if uri:
            _uri = uri
         else:
            assert(self._prefix is not None)
            _uri = "{}.{}".format(self._prefix, func.__name__)

         if inspect.isgeneratorfunction(func):
            func = inlineCallbacks(func)

         self._handlers.append((_uri, func))
         return func
      return decorator


   def signal(self, name):
      """
      Decorator attaching a function as handler for application signals.

      Signals are local events triggered internally and exposed to the
      developer to be able to react to the application lifecycle.

      If the function yield, it will be assumed that it's an asychronous
      coroutine and inlineCallbacks will be applied to it.

      Current signals :

         - `onjoined`: Triggered after the application session has joined the
            realm on the router and registered/subscribed all procedures
            and event handlers that were setup via decorators.
         - `onleave`: Triggered when the application session leaves the realm.

      .. code-block:: python

         @app.signal('onjoined')
         def _():
            # do after the app has join a realm

      :param name: The name of the signal to watch.
      :type name: str
      """
      def decorator(func):
         if inspect.isgeneratorfunction(func):
            func = inlineCallbacks(func)
         self._signals.setdefault(name, []).append(func)
         return func
      return decorator


   @inlineCallbacks
   def _fire_signal(self, name, *args, **kwargs):
      """
      Utility method to call all signal handlers for a given signal.

      :param name: The signal name.
      :type name: str
      """
      for handler in self._signals.get(name, []):
         try:
            ## FIXME: what if the signal handler is not a coroutine?
            ## Why run signal handlers synchronously?
            yield handler(*args, **kwargs)
         except Exception as e:
            ## FIXME
            log.msg("Warning: exception in signal handler swallowed", e)
