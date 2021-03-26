:mod:`autobahn.twisted.testing`
===============================

.. py:module:: autobahn.twisted.testing


Package Contents
----------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.twisted.testing.MemoryReactorClockResolver



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.twisted.testing.create_pumper
   autobahn.twisted.testing.create_memory_agent


.. class:: MemoryReactorClockResolver


   Bases: :class:`twisted.internet.testing.MemoryReactorClock`, :class:`autobahn.twisted.testing._TestNameResolver`

   Combine MemoryReactor, Clock and an IReactorPluggableNameResolver
   together.


.. function:: create_pumper()

   return a new instance implementing IPumper


.. function:: create_memory_agent(reactor, pumper, server_protocol)

   return a new instance implementing `IWebSocketClientAgent`.

   connection attempts will be satisfied by traversing the Upgrade
   request path starting at `resource` to find a `WebSocketResource`
   and then exchange data between client and server using purely
   in-memory buffers.


