:mod:`autobahn.wamp.gen.wamp.proto.Unsubscribe`
===============================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Unsubscribe


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Unsubscribe.Unsubscribe



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Unsubscribe.UnsubscribeStart
   autobahn.wamp.gen.wamp.proto.Unsubscribe.UnsubscribeAddRequest
   autobahn.wamp.gen.wamp.proto.Unsubscribe.UnsubscribeAddSubscription
   autobahn.wamp.gen.wamp.proto.Unsubscribe.UnsubscribeEnd


.. class:: Unsubscribe

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsUnsubscribe(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Request(self)


   .. method:: Subscription(self)



.. function:: UnsubscribeStart(builder)


.. function:: UnsubscribeAddRequest(builder, request)


.. function:: UnsubscribeAddSubscription(builder, subscription)


.. function:: UnsubscribeEnd(builder)


