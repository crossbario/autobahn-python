:mod:`autobahn.twisted.wamp`
============================

.. py:module:: autobahn.twisted.wamp


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.twisted.wamp.ApplicationSession
   autobahn.twisted.wamp.ApplicationSessionFactory
   autobahn.twisted.wamp.ApplicationRunner
   autobahn.twisted.wamp.Application
   autobahn.twisted.wamp.Service
   autobahn.twisted.wamp.Session



.. class:: ApplicationSession(config=None)


   Bases: :class:`autobahn.wamp.protocol.ApplicationSession`

   WAMP application session for Twisted-based applications.

   Implements:

       * :class:`autobahn.wamp.interfaces.ITransportHandler`
       * :class:`autobahn.wamp.interfaces.ISession`

   .. attribute:: log
      

      


.. class:: ApplicationSessionFactory(config=None)


   Bases: :class:`autobahn.wamp.protocol.ApplicationSessionFactory`

   WAMP application session factory for Twisted-based applications.

   .. attribute:: session
      

      The application session class this application session factory will use. Defaults to :class:`autobahn.twisted.wamp.ApplicationSession`.


   .. attribute:: log
      

      


.. class:: ApplicationRunner(url, realm=None, extra=None, serializers=None, ssl=None, proxy=None, headers=None, max_retries=None, initial_retry_delay=None, max_retry_delay=None, retry_delay_growth=None, retry_delay_jitter=None)


   Bases: :class:`object`

   This class is a convenience tool mainly for development and quick hosting
   of WAMP application components.

   It can host a WAMP application component in a WAMP-over-WebSocket client
   connecting to a WAMP router.

   .. attribute:: log
      

      

   .. method:: stop(self)

      Stop reconnecting, if auto-reconnecting was enabled.


   .. method:: run(self, make, start_reactor=True, auto_reconnect=False, log_level='info', endpoint=None, reactor=None)

      Run the application component.

      :param make: A factory that produces instances of :class:`autobahn.twisted.wamp.ApplicationSession`
         when called with an instance of :class:`autobahn.wamp.types.ComponentConfig`.
      :type make: callable

      :param start_reactor: When ``True`` (the default) this method starts
         the Twisted reactor and doesn't return until the reactor
         stops. If there are any problems starting the reactor or
         connect()-ing, we stop the reactor and raise the exception
         back to the caller.

      :returns: None is returned, unless you specify
          ``start_reactor=False`` in which case the Deferred that
          connect() returns is returned; this will callback() with
          an IProtocol instance, which will actually be an instance
          of :class:`WampWebSocketClientProtocol`



.. class:: Application(prefix=None)


   Bases: :class:`object`

   A WAMP application. The application object provides a simple way of
   creating, debugging and running WAMP application components.

   .. attribute:: log
      

      

   .. method:: __call__(self, config)

      Factory creating a WAMP application session for the application.

      :param config: Component configuration.
      :type config: Instance of :class:`autobahn.wamp.types.ComponentConfig`

      :returns: obj -- An object that derives of
         :class:`autobahn.twisted.wamp.ApplicationSession`


   .. method:: run(self, url='ws://localhost:8080/ws', realm='realm1', start_reactor=True)

      Run the application.

      :param url: The URL of the WAMP router to connect to.
      :type url: unicode
      :param realm: The realm on the WAMP router to join.
      :type realm: unicode


   .. method:: register(self, uri=None)

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
      :type uri: unicode


   .. method:: subscribe(self, uri=None)

      Decorator attaching a function as an event handler.

      The first argument of the decorator should be the URI of the topic
      to subscribe to. If no URI is given, the URI is constructed from
      the application URI prefix and the Python function name.

      If the function yield, it will be assumed that it's an asynchronous
      process and inlineCallbacks will be applied to it.

      :Example:

      .. code-block:: python

         @app.subscribe('com.myapp.topic1')
         def onevent1(x, y):
            print("got event on topic1", x, y)

      :param uri: The URI of the topic to subscribe to.
      :type uri: unicode


   .. method:: signal(self, name)

      Decorator attaching a function as handler for application signals.

      Signals are local events triggered internally and exposed to the
      developer to be able to react to the application lifecycle.

      If the function yield, it will be assumed that it's an asynchronous
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
      :type name: unicode


   .. method:: _fire_signal(self, name, *args, **kwargs)

      Utility method to call all signal handlers for a given signal.

      :param name: The signal name.
      :type name: str



.. class:: Service(url, realm, make, extra=None, context_factory=None)


   Bases: :class:`twisted.application.service.MultiService`

   A WAMP application as a twisted service.
   The application object provides a simple way of creating, debugging and running WAMP application
   components inside a traditional twisted application

   This manages application lifecycle of the wamp connection using startService and stopService
   Using services also allows to create integration tests that properly terminates their connections

   It can host a WAMP application component in a WAMP-over-WebSocket client
   connecting to a WAMP router.

   .. attribute:: factory
      

      

   .. method:: setupService(self)

      Setup the application component.



.. class:: Session(config=None)


   Bases: :class:`autobahn.wamp.protocol._SessionShim`

   shim that lets us present pep8 API for user-classes to override,
   but also backwards-compatible for existing code using
   ApplicationSession "directly".

   **NOTE:** this is not public or intended for use; you should import
   either autobahn.asyncio.wamp.Session or
   autobahn.twisted.wamp.Session depending on which async
   framework yo're using.

   .. method:: on_welcome(self, welcome_msg)


   .. method:: on_join(self, details)


   .. method:: on_leave(self, details)


   .. method:: on_connect(self)


   .. method:: on_disconnect(self)



