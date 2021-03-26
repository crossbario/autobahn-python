:mod:`autobahn.wamp.gen.wamp.proto.Unsubscribed`
================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Unsubscribed


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Unsubscribed.Unsubscribed



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Unsubscribed.UnsubscribedStart
   autobahn.wamp.gen.wamp.proto.Unsubscribed.UnsubscribedAddRequest
   autobahn.wamp.gen.wamp.proto.Unsubscribed.UnsubscribedAddSubscription
   autobahn.wamp.gen.wamp.proto.Unsubscribed.UnsubscribedAddReason
   autobahn.wamp.gen.wamp.proto.Unsubscribed.UnsubscribedEnd


.. class:: Unsubscribed

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsUnsubscribed(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Request(self)


   .. method:: Subscription(self)


   .. method:: Reason(self)



.. function:: UnsubscribedStart(builder)


.. function:: UnsubscribedAddRequest(builder, request)


.. function:: UnsubscribedAddSubscription(builder, subscription)


.. function:: UnsubscribedAddReason(builder, reason)


.. function:: UnsubscribedEnd(builder)


