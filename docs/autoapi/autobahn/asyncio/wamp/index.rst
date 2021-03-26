:mod:`autobahn.asyncio.wamp`
============================

.. py:module:: autobahn.asyncio.wamp


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.asyncio.wamp.ApplicationSession
   autobahn.asyncio.wamp.ApplicationSessionFactory
   autobahn.asyncio.wamp.ApplicationRunner



.. class:: ApplicationSession(config=None)


   Bases: :class:`autobahn.wamp.protocol.ApplicationSession`

   WAMP application session for asyncio-based applications.

   Implements:

       * ``autobahn.wamp.interfaces.ITransportHandler``
       * ``autobahn.wamp.interfaces.ISession``

   .. attribute:: log
      

      


.. class:: ApplicationSessionFactory(config=None)


   Bases: :class:`autobahn.wamp.protocol.ApplicationSessionFactory`

   WAMP application session factory for asyncio-based applications.

   .. attribute:: session
      

      The application session class this application session factory will use.
      Defaults to :class:`autobahn.asyncio.wamp.ApplicationSession`.


   .. attribute:: log
      

      


.. class:: ApplicationRunner(url, realm=None, extra=None, serializers=None, ssl=None, proxy=None, headers=None)


   Bases: :class:`object`

   This class is a convenience tool mainly for development and quick hosting
   of WAMP application components.

   It can host a WAMP application component in a WAMP-over-WebSocket client
   connecting to a WAMP router.

   .. attribute:: log
      

      

   .. method:: stop(self)
      :abstractmethod:

      Stop reconnecting, if auto-reconnecting was enabled.


   .. method:: run(self, make, start_loop=True, log_level='info')

      Run the application component. Under the hood, this runs the event
      loop (unless `start_loop=False` is passed) so won't return
      until the program is done.

      :param make: A factory that produces instances of :class:`autobahn.asyncio.wamp.ApplicationSession`
         when called with an instance of :class:`autobahn.wamp.types.ComponentConfig`.
      :type make: callable

      :param start_loop: When ``True`` (the default) this method
          start a new asyncio loop.
      :type start_loop: bool

      :returns: None is returned, unless you specify
          `start_loop=False` in which case the coroutine from calling
          `loop.create_connection()` is returned. This will yield the
          (transport, protocol) pair.



