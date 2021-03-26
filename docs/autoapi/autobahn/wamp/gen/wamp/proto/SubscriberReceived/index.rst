:mod:`autobahn.wamp.gen.wamp.proto.SubscriberReceived`
======================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.SubscriberReceived


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.SubscriberReceived.SubscriberReceived



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.SubscriberReceived.SubscriberReceivedStart
   autobahn.wamp.gen.wamp.proto.SubscriberReceived.SubscriberReceivedAddPublication
   autobahn.wamp.gen.wamp.proto.SubscriberReceived.SubscriberReceivedAddSubscriber
   autobahn.wamp.gen.wamp.proto.SubscriberReceived.SubscriberReceivedAddSubscriberAuthid
   autobahn.wamp.gen.wamp.proto.SubscriberReceived.SubscriberReceivedAddSubscriberAuthrole
   autobahn.wamp.gen.wamp.proto.SubscriberReceived.SubscriberReceivedAddPayload
   autobahn.wamp.gen.wamp.proto.SubscriberReceived.SubscriberReceivedStartPayloadVector
   autobahn.wamp.gen.wamp.proto.SubscriberReceived.SubscriberReceivedAddEncAlgo
   autobahn.wamp.gen.wamp.proto.SubscriberReceived.SubscriberReceivedAddEncSerializer
   autobahn.wamp.gen.wamp.proto.SubscriberReceived.SubscriberReceivedAddEncKey
   autobahn.wamp.gen.wamp.proto.SubscriberReceived.SubscriberReceivedStartEncKeyVector
   autobahn.wamp.gen.wamp.proto.SubscriberReceived.SubscriberReceivedEnd


.. class:: SubscriberReceived

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsSubscriberReceived(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Publication(self)


   .. method:: Subscriber(self)


   .. method:: SubscriberAuthid(self)


   .. method:: SubscriberAuthrole(self)


   .. method:: Payload(self, j)


   .. method:: PayloadAsNumpy(self)


   .. method:: PayloadLength(self)


   .. method:: EncAlgo(self)


   .. method:: EncSerializer(self)


   .. method:: EncKey(self, j)


   .. method:: EncKeyAsNumpy(self)


   .. method:: EncKeyLength(self)



.. function:: SubscriberReceivedStart(builder)


.. function:: SubscriberReceivedAddPublication(builder, publication)


.. function:: SubscriberReceivedAddSubscriber(builder, subscriber)


.. function:: SubscriberReceivedAddSubscriberAuthid(builder, subscriberAuthid)


.. function:: SubscriberReceivedAddSubscriberAuthrole(builder, subscriberAuthrole)


.. function:: SubscriberReceivedAddPayload(builder, payload)


.. function:: SubscriberReceivedStartPayloadVector(builder, numElems)


.. function:: SubscriberReceivedAddEncAlgo(builder, encAlgo)


.. function:: SubscriberReceivedAddEncSerializer(builder, encSerializer)


.. function:: SubscriberReceivedAddEncKey(builder, encKey)


.. function:: SubscriberReceivedStartEncKeyVector(builder, numElems)


.. function:: SubscriberReceivedEnd(builder)


