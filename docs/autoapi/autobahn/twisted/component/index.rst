:mod:`autobahn.twisted.component`
=================================

.. py:module:: autobahn.twisted.component


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.twisted.component.Component



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.twisted.component.run


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

      This is so we can just return False if we didn't import any
      TLS/SSL libraries. Otherwise, returns True if this is an
      OpenSSL.SSL.Error


   .. method:: _check_native_endpoint(self, endpoint)


   .. method:: _connect_transport(self, reactor, transport, session_factory, done)

      Create and connect a WAMP-over-XXX transport.

      :param done: is a Deferred/Future from the parent which we
          should signal upon error if it is not done yet (XXX maybe an
          "on_error" callable instead?)


   .. method:: start(self, reactor=None)

      This starts the Component, which means it will start connecting
      (and re-connecting) to its configured transports. A Component
      runs until it is "done", which means one of:
      - There was a "main" function defined, and it completed successfully;
      - Something called ``.leave()`` on our session, and we left successfully;
      - ``.stop()`` was called, and completed successfully;
      - none of our transports were able to connect successfully (failure);

      :returns: a Deferred that fires (with ``None``) when we are
          "done" or with a Failure if something went wrong.



.. function:: run(components, log_level='info')

   High-level API to run a series of components.

   This will only return once all the components have stopped
   (including, possibly, after all re-connections have failed if you
   have re-connections enabled). Under the hood, this calls
   :meth:`twisted.internet.reactor.run` -- if you wish to manage the
   reactor loop yourself, use the
   :meth:`autobahn.twisted.component.Component.start` method to start
   each component yourself.

   :param components: the Component(s) you wish to run
   :type components: instance or list of :class:`autobahn.twisted.component.Component`

   :param log_level: a valid log-level (or None to avoid calling start_logging)
   :type log_level: string


