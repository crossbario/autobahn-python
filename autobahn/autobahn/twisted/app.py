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

"""
   Flask-like syntaxe for WAMP projects.

   This is intended to make it easier to start with autobahn/crossbar.io
   and abstract a lot of things : you don't have to think about the main
   loop, the application session class lifecycle, etc.

   It lets you react, using callback defined via decorators, to 3 things :
      - PUB/SUB events : regular WAMP PUB/SUB events.
      - RPC calls : expose a function as callable from the outside.
      - app signals : internal app events allowing you to react to the app
                      lifecycle.

   :Example:

      from autobahn.twisted.app import Application
      from autobahn.wamp.types import PublishOptions

      app = Application()

      # Register a function to allow calling it from outside
      # via RPC
      @app.register('a_procedure_name')
      def a_procedure(arg1, arg2):
         print('The procedure is called with these arguments :')
         print(arg1, arg2)
         # publish the event
         app.session.publish('an_event',
                             "Some data attached to the event",
                            # force publisher to receive its
                            # own event
                            options=PublishOptions(excludeMe=False))

      # Register a callback that will be called when the
      # event 'an_event' is triggered
      @app.subscribe('an_event')
      def an_event(val):
         print('Received an event with something :')
         print(val)

      # This will be called once the application is connected
      # to the server
      @app.signal('onjoin')
      def entry_point():
         print('The application is connected !')
         # Calling a_procedure()
         app.session.call('a_procedure_name', True, False)

      if __name__ == "__main__":
          # By default, the application run on port 8080
          print('Before the app start')
          app.run()

      # Now, in a Terminal:

      ## $ python script.py
      ## Running on 'ws://localhost:8080'
      ## Before the app start
      ## The application is connected !
      ## The procedure is called with these arguments :
      ## (True, False)
      ## Received an event with something :
      ## Some data attached to the event

   Ok, this example is cheating a little bit because the application triggers
   events and listen to them, and it calls it's own code via RPC. You may want
   to call them from a Web page using autobahn.js (http://autobahn.ws/js/) for
   a more convincing demo.

   If you use "yield" inside any of the callbacks, `@inlineCallbacks` will
   be applied automatically. It means every yielded line will be be added in
   a Defered so they execute sequencially, in regards to the other yielded
   lines in the same function. In that case, you should not `return`, but use
   `returnValue`.

   E.G :

      from autobahn.twisted.app import Application

      from twisted.internet.defer import returnValue
      from twisted.web.client import Agent

      app = Application()

      @app.register('statuscode')
      def statuscode(url):
         ''' Return the status code of a GET request on a URL '''

         # Little hack to add asynchronous requests to our app
         # It's not very clean, but for the example, it will do :)
         from twisted.internet import reactor
         agent = Agent(reactor)

         # Asynchronous GET request on the url
         d = yield agent.request('GET', url)

         # Using returnValue and not return because the whole
         # procedure is a coroutine since we used yield.
         returnValue(d.code)

      @app.signal('onjoin')
      def entry_point():
         # Calling statuscode
         url = "http://tavendo.com"
         code = yield app.session.call('statuscode', url)
         print("GET on '%s' returned status '%s'" % (url, code))

      if __name__ == "__main__":
          app.run()

      # Now, in a Terminal:
      ## python script.py
      ## Running on 'ws://localhost:8080'
      ## GET on 'http://tavendo.com' returned status '200'

"""

from __future__ import absolute_import

import inspect

from twisted.python import log
from twisted.internet.defer import inlineCallbacks

from autobahn.wamp import types
from autobahn.twisted.wamp import ApplicationSession, \
                                  ApplicationRunner


class _ApplicationSession(ApplicationSession):

   def __init__(self, config, app):
      ApplicationSession.__init__(self, config)
      self.app = app


   @inlineCallbacks
   def onJoin(self, details):

      for uri, proc in self.app._procs:
         self.app._fire_signal('onregister', uri, proc)
         yield self.register(proc, uri)

      for uri, handler in self.app._handlers:
         self.app._fire_signal('onsubscribe', uri, func)
         yield self.subscribe(handler, uri)

      yield self.app._fire_signal('onjoin')



class Application(object):
   """ Self contained autobahn application, including it's own server.

      See module docstring for usage.
   """

   def __init__(self, prefix = None):
      """
      Ctor.

      :param prefix: The application URI prefix to use, e.g. `com.example.myapp`.
      :type prefix: str
      """
      self.session = None
      self._prefix = prefix
      self._procs = []
      self._handlers = []
      self._signals = {}


   def __call__(self, config):
      """
      Factory creating the application session.

      :param config: Component configuration.
      :type config: instance of :class:`autobahn.wamp.types.ComponentConfig`

      :returns: obj -- An object that derives of :class:`autobahn.twisted.wamp.ApplicationSession`
      """
      assert(self.session is None)
      self.session = _ApplicationSession(config, self)
      return self.session


   def run(self, url = "ws://localhost:8080",
           realm = "realm1", standalone = True):
      print("Running on '%s'" % url)
      runner = ApplicationRunner(url, realm, standalone = standalone)
      runner.run(self.__call__)


   def register(self, uri = None):
      """ Decorator exposing a function as a remote callable procedure.

         The function will be bound as a RPC handler in onJoin().

         E.G:

            @app.register('add')
            def add(a, b):
               return a + b

         The URI doesn't have to be the same as the function name. You can do :

            @app.register('add')
            def _(a, b):
               return a + b

         If you don't pass a URI, the function name will be used as such :

            # URI will be 'add'
            @app.register()
            def add(a, b):
               return a + b

         If your application has a prefix, it will be prepended to the URI :

            app = Application('com.yoursite.yourapp')

            # URI will be 'com.yoursite.yourapp.add'
            @app.register('add')
            def _(a, b):
               return a + b

         If the function yield, it will be assumed that it's an asychronous
         process and `@inlineCallbacks` will be applied to it. In that case, if
         you wish to return something, you should use `returnValue` :

         E.G:

            from twisted.internet.defer import returnValue

            @app.register()
            def add(a, b):
               res = yield stuff(a, b)
               returnValue(res)

         :param uri: The URI (remote procedure name)
                     this callback is related to.
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
      """ Decorator attaching a function as an event callback.

         The function arguments will be data attached to the event.

         E.G:

            @app.subscribe('event_name')
            def add(a, b):
               return a + b

         The first argument of the decorator should be the event name.

         If the function yield, it will be assumed that it's an asychronous
         process and inlineCallbacks will be applied to it.

         :param uri: The URI (event name)
                     this callback is related to.
         :type uri: str

      """
      def decorator(func):

         if inspect.isgeneratorfunction(func):
            func = inlineCallbacks(func)

         self._handlers.append((uri, func))
         return func
      return decorator


   def signal(self, name):
      """ Decorator attaching a function as an app signal callback.

         Signals are local events triggered internally and exposed
         to the developper to be able to react to the application lifecycle.

         Arguments will be data attached to the signal.

         E.G:

            @app.signal('onjoin')
            def _():
               # do after the app has join a realm

         If the function yield, it will be assumed that it's an asychronous
         coroutine and inlineCallbacks will be applied to it.

         Current signals :

            - onregister : when a callback RPC is registered.
                           Params:
                              * uri : the RPC uri.
                              * func : the RPC callback.

            - onsubscribe : when a event handler is registered.
                            Params:
                               * uri : the RPC uri.
                               * func : the RPC callback.
            - onjoin : after the app connected to the router and made all
                       the RPC registration and PUB/SUB subcricptions.

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
