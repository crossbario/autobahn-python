:mod:`autobahn.asyncio.component`
=================================

.. py:module:: autobahn.asyncio.component


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.asyncio.component.Component



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.asyncio.component.run


.. class:: Component(main=None, transports=None, config=None, realm='realm1', extra=None, authentication=None, session_factory=None, is_fatal=None)


   Bases: :class:`autobahn.wamp.component.Component`

   A component establishes a transport and attached a session
   to a realm using the transport for communication.

   The transports a component tries to use can be configured,
   as well as the auto-reconnect strategy.

   .. attribute:: log
      

      

   .. attribute:: session_factory
      

      The factory of the session we will instantiate.


   .. method:: _is_ssl_error(self, e)

      Internal helper.


   .. method:: _check_native_endpoint(self, endpoint)


   .. method:: _connect_transport(self, loop, transport, session_factory, done)

      Create and connect a WAMP-over-XXX transport.


   .. method:: _wrap_connection_future(self, transport, done, conn_f)


   .. method:: start(self, loop=None)

      This starts the Component, which means it will start connecting
      (and re-connecting) to its configured transports. A Component
      runs until it is "done", which means one of:
      - There was a "main" function defined, and it completed successfully;
      - Something called ``.leave()`` on our session, and we left successfully;
      - ``.stop()`` was called, and completed successfully;
      - none of our transports were able to connect successfully (failure);

      :returns: a Future which will resolve (to ``None``) when we are
          "done" or with an error if something went wrong.



.. function:: run(components, start_loop=True, log_level='info')

   High-level API to run a series of components.

   This will only return once all the components have stopped
   (including, possibly, after all re-connections have failed if you
   have re-connections enabled). Under the hood, this calls

   XXX fixme for asyncio

   -- if you wish to manage the loop yourself, use the
   :meth:`autobahn.asyncio.component.Component.start` method to start
   each component yourself.

   :param components: the Component(s) you wish to run
   :type components: instance or list of :class:`autobahn.asyncio.component.Component`

   :param start_loop: When ``True`` (the default) this method
       start a new asyncio loop.
   :type start_loop: bool

   :param log_level: a valid log-level (or None to avoid calling start_logging)
   :type log_level: string


