:mod:`autobahn.wamp.gen.wamp.proto.Event`
=========================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Event


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Event.Event



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Event.EventStart
   autobahn.wamp.gen.wamp.proto.Event.EventAddSubscription
   autobahn.wamp.gen.wamp.proto.Event.EventAddPublication
   autobahn.wamp.gen.wamp.proto.Event.EventAddArgs
   autobahn.wamp.gen.wamp.proto.Event.EventStartArgsVector
   autobahn.wamp.gen.wamp.proto.Event.EventAddKwargs
   autobahn.wamp.gen.wamp.proto.Event.EventStartKwargsVector
   autobahn.wamp.gen.wamp.proto.Event.EventAddPayload
   autobahn.wamp.gen.wamp.proto.Event.EventStartPayloadVector
   autobahn.wamp.gen.wamp.proto.Event.EventAddEncAlgo
   autobahn.wamp.gen.wamp.proto.Event.EventAddEncSerializer
   autobahn.wamp.gen.wamp.proto.Event.EventAddEncKey
   autobahn.wamp.gen.wamp.proto.Event.EventStartEncKeyVector
   autobahn.wamp.gen.wamp.proto.Event.EventAddPublisher
   autobahn.wamp.gen.wamp.proto.Event.EventAddPublisherAuthid
   autobahn.wamp.gen.wamp.proto.Event.EventAddPublisherAuthrole
   autobahn.wamp.gen.wamp.proto.Event.EventAddTopic
   autobahn.wamp.gen.wamp.proto.Event.EventAddRetained
   autobahn.wamp.gen.wamp.proto.Event.EventAddAcknowledge
   autobahn.wamp.gen.wamp.proto.Event.EventAddForwardFor
   autobahn.wamp.gen.wamp.proto.Event.EventStartForwardForVector
   autobahn.wamp.gen.wamp.proto.Event.EventEnd


.. class:: Event

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsEvent(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Subscription(self)


   .. method:: Publication(self)


   .. method:: Args(self, j)


   .. method:: ArgsAsNumpy(self)


   .. method:: ArgsLength(self)


   .. method:: Kwargs(self, j)


   .. method:: KwargsAsNumpy(self)


   .. method:: KwargsLength(self)


   .. method:: Payload(self, j)


   .. method:: PayloadAsNumpy(self)


   .. method:: PayloadLength(self)


   .. method:: EncAlgo(self)


   .. method:: EncSerializer(self)


   .. method:: EncKey(self, j)


   .. method:: EncKeyAsNumpy(self)


   .. method:: EncKeyLength(self)


   .. method:: Publisher(self)


   .. method:: PublisherAuthid(self)


   .. method:: PublisherAuthrole(self)


   .. method:: Topic(self)


   .. method:: Retained(self)


   .. method:: Acknowledge(self)


   .. method:: ForwardFor(self, j)


   .. method:: ForwardForLength(self)



.. function:: EventStart(builder)


.. function:: EventAddSubscription(builder, subscription)


.. function:: EventAddPublication(builder, publication)


.. function:: EventAddArgs(builder, args)


.. function:: EventStartArgsVector(builder, numElems)


.. function:: EventAddKwargs(builder, kwargs)


.. function:: EventStartKwargsVector(builder, numElems)


.. function:: EventAddPayload(builder, payload)


.. function:: EventStartPayloadVector(builder, numElems)


.. function:: EventAddEncAlgo(builder, encAlgo)


.. function:: EventAddEncSerializer(builder, encSerializer)


.. function:: EventAddEncKey(builder, encKey)


.. function:: EventStartEncKeyVector(builder, numElems)


.. function:: EventAddPublisher(builder, publisher)


.. function:: EventAddPublisherAuthid(builder, publisherAuthid)


.. function:: EventAddPublisherAuthrole(builder, publisherAuthrole)


.. function:: EventAddTopic(builder, topic)


.. function:: EventAddRetained(builder, retained)


.. function:: EventAddAcknowledge(builder, acknowledge)


.. function:: EventAddForwardFor(builder, forwardFor)


.. function:: EventStartForwardForVector(builder, numElems)


.. function:: EventEnd(builder)


