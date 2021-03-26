:mod:`autobahn.wamp.gen.wamp.proto.EventReceived`
=================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.EventReceived


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.EventReceived.EventReceived



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.EventReceived.EventReceivedStart
   autobahn.wamp.gen.wamp.proto.EventReceived.EventReceivedAddPublication
   autobahn.wamp.gen.wamp.proto.EventReceived.EventReceivedAddPayload
   autobahn.wamp.gen.wamp.proto.EventReceived.EventReceivedStartPayloadVector
   autobahn.wamp.gen.wamp.proto.EventReceived.EventReceivedAddEncAlgo
   autobahn.wamp.gen.wamp.proto.EventReceived.EventReceivedAddEncSerializer
   autobahn.wamp.gen.wamp.proto.EventReceived.EventReceivedAddEncKey
   autobahn.wamp.gen.wamp.proto.EventReceived.EventReceivedStartEncKeyVector
   autobahn.wamp.gen.wamp.proto.EventReceived.EventReceivedEnd


.. class:: EventReceived

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsEventReceived(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Publication(self)


   .. method:: Payload(self, j)


   .. method:: PayloadAsNumpy(self)


   .. method:: PayloadLength(self)


   .. method:: EncAlgo(self)


   .. method:: EncSerializer(self)


   .. method:: EncKey(self, j)


   .. method:: EncKeyAsNumpy(self)


   .. method:: EncKeyLength(self)



.. function:: EventReceivedStart(builder)


.. function:: EventReceivedAddPublication(builder, publication)


.. function:: EventReceivedAddPayload(builder, payload)


.. function:: EventReceivedStartPayloadVector(builder, numElems)


.. function:: EventReceivedAddEncAlgo(builder, encAlgo)


.. function:: EventReceivedAddEncSerializer(builder, encSerializer)


.. function:: EventReceivedAddEncKey(builder, encKey)


.. function:: EventReceivedStartEncKeyVector(builder, numElems)


.. function:: EventReceivedEnd(builder)


