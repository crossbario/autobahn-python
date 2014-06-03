# -*- coding: utf-8 -*-

"""
   Application, flask-like, syntaxe for WAMP projects.

   This is intended to make it easier to start with autobahn/crossbar.io
   and abstract a lot of things : you don't have to think about the main
   loop, the application session class lifecycle, the publish options wrapper,
   etc.

   It essentially all you to react (using callback defined via decorators) to
   3 things :
      - PUB/SUB events : regular WAMP PUB/SUB events.
      - RPC calls : expose a function as callable from the outside.
      - app signals : internal app events allowing you to react to the app
                      lifecycle.

   :Example:

      from autobahn.twisted.app import Application

      # by default, the application run on port 8080
      app = Application("your_project_name")

      # register a function to allow calling from outside
      # via RPC
      @app.register('success')
      def a_procedure(context, arg1, arg2):
         print(arg1, arg2)
         # publish the event
         context.publish('an_event', "Hello !",
                         # force publisher to receive its
                         # own event
                         options={"excludeMe": False})

      # register a callback that will be called with the
      # event 'an_event' is triggered
      @app.subscribe('an_event')
      def an_event(context, val):
         print(val)

      # This will be called once the application is connecter
      # to the server
      @app.signal('onjoin')
      def entry_point(context):
         print('Starting demo !')
         context.call('success', True, False)

      if __name__ == "__main__":
          app.run()

      # Now, in a Terminal:

      ## $ python script.py
      ## Starting demo !
      ## True False
      ## Hello !

   If you use "yield" inside any of the callbacks, inlineCallbacks will
   be applied automatically. It means every yielded line will be be added in
   a Defered so they execute sequencially, in regards to the other yielded
   lines in the same function.

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
         yield self.register(proc, uri)

      for uri, handler in self.app._handlers:
         yield self.subscribe(handler, uri)

      yield self.app._fire_signal('onpostjoin')



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


   def run(self, url, realm, standalone = False):
      runner = ApplicationRunner(url, realm, standalone = standalone)
      runner.run(self.__call__)


   def register(self, uri = None):
      """ Decorator exposing a function as a remote callable procedure.

         The function will be bind as a RPC handler in onJoin().

         The function must accept the a dictionary as 1st arg,
         containing information to the current context such as a reference to
         the app and the RPC URI.

         Other arguments will be the regular function parameters.

         E.G:

            @app.register('example.tools.add')
            def add(context, a, b):
               return a + b

         If the function yield, it will be assumed that it's an asychronous
         process and inlineCallbacks will be applied to it.

         The first argument of the decorator should be the procedure name. If
         you ommit it, a name will be generated for you using the pattern :
         <module>.<func_name>.

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

         self._fire_signal('onregister', _uri, func)

         if inspect.isgeneratorfunction(func):
            func = inlineCallbacks(func)

         self._procs.append((_uri, func))
         return func
      return decorator


   def subscribe(self, uri = None):
      """ Decorator attaching a function as an event callback.

         The function must accept the a dictionary as 1st arg,
         containing information to the current context such as a reference to
         the app and the RPC URI.

         Other arguments will be data attached to the event.

         E.G:

            @app.subscribe('procedure_name')
            def add(context, a, b):
               return a + b

         If the function yield, it will be assumed that it's an asychronous
         process and inlineCallbacks will be applied to it.

         :param uri: The URI (event name)
                     this callback is related to.
         :type uri: str
      """
      def decorator(func):
         if uri:
            _uri = uri
         else:
            assert(self._prefix is not None)
            _uri = "{}.{}".format(self._prefix, func.__name__)

         self._fire_signal('onsubscribe', _uri, func)

         if inspect.isgeneratorfunction(func):
            func = inlineCallbacks(func)

         self._handlers.append((_uri, func))
         return func
      return decorator


   def signal(self, name):
      """ Decorator attaching a function as an app signal callback.

         Signals are internal events internally to react the
          application lifecycle.

         The function must accept the a dictionary as 1st arg,
         containing information to the current context such as a reference to
         the app and the RPC URI.

         Other arguments will be data attached to the signal.

         E.G:

            @app.signal('onpostjoin')
            def add(context):
               # do after the app has join a realm

         If the function yield, it will be assumed that it's an asychronous
         process and inlineCallbacks will be applied to it.

         Current signals :

            - onrun : when the main loop is about to start.
                      Params :
                        * mode : "client" or "server" depending on debug's value
                        * runner = if "client", the current application runner
                        * reactor = if "server", the current reactor
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
