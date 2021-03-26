:mod:`autobahn.twisted.util`
============================

.. py:module:: autobahn.twisted.util


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.twisted.util.sleep
   autobahn.twisted.util.peer2str
   autobahn.twisted.util.transport_channel_id


.. data:: PipeAddress
   

   

.. data:: _HAS_IPV6
   :annotation: = True

   

.. data:: __all
   :annotation: = ['sleep', 'peer2str', 'transport_channel_id']

   

.. function:: sleep(delay, reactor=None)

   Inline sleep for use in co-routines (Twisted ``inlineCallback`` decorated functions).

   .. seealso::
      * `twisted.internet.defer.inlineCallbacks <http://twistedmatrix.com/documents/current/api/twisted.internet.defer.html#inlineCallbacks>`__
      * `twisted.internet.interfaces.IReactorTime <http://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IReactorTime.html>`__

   :param delay: Time to sleep in seconds.
   :type delay: float
   :param reactor: The Twisted reactor to use.
   :type reactor: None or provider of ``IReactorTime``.


.. function:: peer2str(addr)

   Convert a Twisted address as returned from ``self.transport.getPeer()`` to a string.

   :returns: Returns a string representation of the peer on a Twisted transport.
   :rtype: unicode


.. function:: transport_channel_id(transport: object, is_server: bool, channel_id_type: Optional[str] = None) -> bytes


