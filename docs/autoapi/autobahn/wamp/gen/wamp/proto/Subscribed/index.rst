:mod:`autobahn.wamp.gen.wamp.proto.Subscribed`
==============================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Subscribed


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Subscribed.Subscribed



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Subscribed.SubscribedStart
   autobahn.wamp.gen.wamp.proto.Subscribed.SubscribedAddRequest
   autobahn.wamp.gen.wamp.proto.Subscribed.SubscribedAddSubscription
   autobahn.wamp.gen.wamp.proto.Subscribed.SubscribedEnd


.. class:: Subscribed

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsSubscribed(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Request(self)


   .. method:: Subscription(self)



.. function:: SubscribedStart(builder)


.. function:: SubscribedAddRequest(builder, request)


.. function:: SubscribedAddSubscription(builder, subscription)


.. function:: SubscribedEnd(builder)


