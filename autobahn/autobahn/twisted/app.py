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

from __future__ import print_function

import inspect

from functools import partial

from twisted.python import log
from twisted.internet.endpoints import serverFromString
from twisted.internet.defer import inlineCallbacks

from autobahn.wamp import types
from autobahn.twisted.websocket import WampWebSocketServerFactory
from autobahn.twisted.choosereactor import install_reactor
from autobahn.wamp.router import RouterFactory
from autobahn.twisted.wamp import (RouterSessionFactory, ApplicationSession,
                                   ApplicationRunner)

class WampAppError(Exception):
   """
      Convenience wrapper around Exception so you can
      catch specifically error raised in the app.py module.
   """
   pass


class Context(object):
   """ Convenience wrapper to be past to app callbacks containing a reference
      to the app object, the uri targetting this callback and some
      convenience methods.

      :param app: The application this callback is related to.
      :type app: Application
      :param uri: The URI (event name, procedure name, signal name...)
                  this callback is related to.
      :type uri: str
   """
   def __init__(self, app, uri):
      self.app = app
      self.url = uri

   @property
   def log(self):
      """ Proxy call to the log method to the current app object.

         This is a convenience method to make logging from inside callbacks
         easier.

         :param str: the message to log.
         :type realm: str
      """
      return self.app.log


   def call(self, uri, *args, **kwargs):
      """ Proxy call to the call method to the current session object.

         This is a convenience method to make RPC from inside callbacks
         easier.

         :param uri: The application this callback is related to.
         :type app: Application
         :param *args, **kwargs: Arguments proxied to the procuedure called.
      """
      return self.app.session.call(uri, *args, **kwargs)

   def publish(self, uri, *args, **kwargs):
      """ Proxy call to the publish method to the current session object.

         This is a convenience method to make event publishing from inside
         callbacks easier.

         :param uri: The application this callback is related to.
         :type app: Application

         :param options: Dictionary of options regarding the treatment of the
                         event. Available options are :

             acknowledge (bool) – If True, this function will return a Defered.
                                  Default is False.
             excludeMe (bool) – If True, exclude the publisher from receiving
                                the event. DEFAULT IS TRUE !
             exclude (list) – List of WAMP session IDs to exclude from receiving
                              this event (blacklist).
             eligible (list) – List of WAMP session IDs eligible to
                               receive this event (whitelist)
             discloseMe (bool) – If True, request to disclose the publisher of
                                  this event to subscribers.

         If you don't receive an event you are subscribing to, chances are
         you are subscribing to this event from the client publishing this
         same event without settings excludeMe to False.

         :param *args, **kwargs: Arguments proxied to the event callbacks.
      """
      options = kwargs.pop('options')
      if not options:
         return self.app.session.publish(uri, *args, **kwargs)

      return self.app.session.publish(uri,
                                      options=types.PublishOptions(**options),
                                      *args, **kwargs)

class WampApplicationSession(ApplicationSession):
   """ Extend the regular Application session, to have the notion of app.

      This supposes that the config object you pass to it contains a reference
      to the application object in config.extra['app'].

      :param config: Application session configuration object. It MUST contains
                     a reference to the related Application instance in
                     config.extra['app'].
      :type app: types.ComponentConfig

      Sessions hold several useful references :
         - self.app : the current Application instance;
         - self.id : the session id provided by the router (None until 'onjoin');
         - self.authid : the client authentification id
                         (None until 'onjoin' or if the client is anonymous);
         - self.authrole : the client authentification role
                          (None until 'onjoin' or if the client is anonymous);
         - self.authmethod : the client authentification method
                          (None until 'onjoin' or if the client is anonymous);
   """

   def __init__(self, config):
      ApplicationSession.__init__(self)
      self.config = config
      self.app = config.extra['app']
      self.app.session = self
      self.id = self.authid = self.authrole = self.authmethod = None

   @inlineCallbacks
   def onJoin(self, details):
      """ Register callacks for RPC and PUB/SUB

         This method is automatically called when the client
         has connected to the router and has joined a realm.

         It will attach all functions registered with @register as
         callbacks for RPC calls for the proper URIs and do the same for
         PUB/SUB handlers registred using @subscribe.

         This method triggers 2 signals :

            - onprejoin() : at the begining of the call;
            - onpostjoin() : at the end of the call.

         This method publishes one event :

            - autobahn.app.%(appname)s.postjoin(handlers) :
                        handlers is the list of all procedures and events
                        for which there is a callback.

         :param details: Informations about the connection
                        (session id, realm, etc)
         :type details: SessionDetails
      """

      self.app.log("Application '%s' connected to '%s' on realm '%s'" % (
                     self.app.name, self.app.connect_to, self.app.realm))

      self.id = details.session
      self.authid = details.authid
      self.authrole = details.authrole
      self.authmethod = details.authmethod

      handlers = {'rpc': [], 'pub_sub': []}
      for uri, proc in self.app.rpc_handlers:
         self.app.log('Registering procedure "%s"' % uri)
         yield self.register(proc, uri)
         handlers['rpc'].append(uri)

      for uri, handler in self.app.event_handlers:
         self.app.log('Adding a subscriber to "%s"' % uri)
         yield self.subscribe(handler, uri)
         handlers['pub_sub'].append(uri)

      yield self.app.call_signal_handlers('onjoin')
      yield self.publish('autobahn.app.%s.postjoin' % self.app.name, handlers)


class Application(object):
   """ Self contained autobahn application, including it's own server.

      See module docstring for usage.
   """

   def __init__(self, name, connect_to="ws://localhost:8080",
                endpoint="tcp:8080", realm="realm1", debug=True, logging=None):
      """
         :param name: A unique name for your app that will be used as a
                     namespace for events.
         :type name: str
         :param connect_to: Router URI for the client to connect
                            to if debug=False.
         :type connect_to: str
         :param endpoint: socket to listen to for the embeded router if
                          debug=True.
         :type endpoint: str
         :param realm: event namespace to join at connection. Clients can only
                       see and do RPC and PUB/SUB with other
                       clients on the same realm1.
         :type realm: str
         :param debug: if True, run stand alone router and embded the app
                       client in it, so you don't have to setup a full
                       router yourself such as crossbar during dev.
         :type debug: bool
         :param debug: if False, calls to self.(log|err) do nothing. If None,
                       will be set to the same value as self.debug.
         :type debug: bool

      """
      self.connect_to = connect_to

      self.name = name
      self.endpoint = endpoint
      self.debug = debug
      self.realm = realm
      self.rpc_handlers = []
      self.event_handlers = []
      self.signal_handlers = {}
      self._session_conf = types.ComponentConfig(realm=self.realm,
                                                extra={'app': self})

      # settings up logging facilities
      self.logging = logging
      if self.logging is None:
         self.logging = self.debug

      if self.logging:
         self._log = partial(log.msg, "<%s> " % self.name)
      else:
         self._log = lambda x: None

   def __call__(self, config):
      """ Wrapper for self.create_session so it can be used by Crossbar """
      if config.extra is None:
        config.extra = {}
      if 'app' not in config.extra:
        config.extra['app'] = self
      self.log(config.__dict__)
      session = self.create_session(config)
      self.log(session.__dict__)
      return session

   @property
   def log(self):
      """ Proxy to twisted logging facilities.

         All messages are prefixed with the app name.

         Log only if self.log = True.

         :param str: the message to log.
         :type realm: str
      """
      return self._log

   def create_session(self, config=None):
      """ Return the ApplicationSession this app will use. """
      return WampApplicationSession(config or self._session_conf)

   def run(self, connect_to=None,  endpoint=None, realm=None, debug=None):
      """ Run the application main loop.

         All params default values equal to the value passed in __init__. You
         can pass them again here to override them just for this call, for
         things like setting up your app using command line arguments.

         :param connect_to: Router URI for the client to connect
                            to if debug=False.
         :type connect_to: str
         :param endpoint: socket to listen to for the embeded router if
                          debug=True.
         :type endpoint: str
         :param realm: event namespace to join at connection. Clients can only
                       see and do RPC and PUB/SUB with other
                       clients on the same realm1.
         :type realm: str
         :param debug: if True, run stand alone router and embded the app
                       client in it, so you don't have to setup a full
                       router yourself such as crossbar during dev.
         :type debug: bool
      """
      connect_to = connect_to or self.connect_to
      endpoint = endpoint or self.endpoint
      realm = realm or self.realm
      if debug is None:
         debug = self.debug

      if not self.debug:
         runner = ApplicationRunner(self.connect_to, self.realm,
                                    extra={'app': self}, debug=self.debug)
         self.call_signal_handlers('onrun', mode="client", runner=runner)
         self.log("Running in client mode. Router URI: %s" % self.connect_to)
         runner.run(WampApplicationSession)
      else:
         # we use an Autobahn utility to install the "best" available Twisted reactor
         reactor = install_reactor()
         router_factory = RouterFactory()
         session_factory = RouterSessionFactory(router_factory)
         # create and add an WAMP application session to run next to the router
         session_factory.add(WampApplicationSession(self._session_conf))
         # create a WAMP-over-WebSocket transport server factory
         transport_factory = WampWebSocketServerFactory(session_factory,
                                                        debug_wamp=self.debug)
         # failByDrop close the TCP connection without a clean handshare
         # it's used for performance, but we prefer a clean standard
         # conformance for dev
         transport_factory.setProtocolOptions(failByDrop=False)
         server = serverFromString(reactor, self.endpoint)
         server.listen(transport_factory)
         self.call_signal_handlers('onrun', mode="server", reactor=reactor)
         self.log("Running in router mode. Local endpoint: %s" % self.endpoint)
         reactor.run()


   def register(self, uri=None):
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
         name = func.__module__ + "." + func.__name__ if uri is None else uri
         if name.startswith('wamp'):
            raise WampAppError('URI cannot start by "wamp"')

         self.call_signal_handlers('onregister', name, func)

         if inspect.isgeneratorfunction(func):
               func = inlineCallbacks(func)
         func = partial(func, Context(self, uri))
         self.rpc_handlers.append((name, func))
         return func
      return decorator

   def subscribe(self, uri):
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
         name = func.__module__ + "." + func.__name__ if uri is None else uri
         if name.startswith('wamp'):
            raise WampAppError('URI cannot start by "wamp"')

         self.call_signal_handlers('onsubscribe', name, func)

         if inspect.isgeneratorfunction(func):
               func = inlineCallbacks(func)

         func = partial(func, Context(self, name))

         self.event_handlers.append((name, func))
         return func
      return decorator

   def signal(self, uri):
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
         func = partial(func, Context(self, uri))
         self.signal_handlers.setdefault(uri, []).append(func)
         return func
      return decorator

   @inlineCallbacks
   def call_signal_handlers(self, name, *args, **kwargs):
      """ Utility method to call all signal handlers for a given signal. """
      for handler in self.signal_handlers.get(name, []):
         yield handler(*args, **kwargs)


