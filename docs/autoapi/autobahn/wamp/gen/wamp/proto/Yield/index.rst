:mod:`autobahn.wamp.gen.wamp.proto.Yield`
=========================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Yield


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Yield.Yield



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Yield.YieldStart
   autobahn.wamp.gen.wamp.proto.Yield.YieldAddRequest
   autobahn.wamp.gen.wamp.proto.Yield.YieldAddPayload
   autobahn.wamp.gen.wamp.proto.Yield.YieldStartPayloadVector
   autobahn.wamp.gen.wamp.proto.Yield.YieldAddEncAlgo
   autobahn.wamp.gen.wamp.proto.Yield.YieldAddEncSerializer
   autobahn.wamp.gen.wamp.proto.Yield.YieldAddEncKey
   autobahn.wamp.gen.wamp.proto.Yield.YieldStartEncKeyVector
   autobahn.wamp.gen.wamp.proto.Yield.YieldEnd


.. class:: Yield

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsYield(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Request(self)


   .. method:: Payload(self, j)


   .. method:: PayloadAsNumpy(self)


   .. method:: PayloadLength(self)


   .. method:: EncAlgo(self)


   .. method:: EncSerializer(self)


   .. method:: EncKey(self, j)


   .. method:: EncKeyAsNumpy(self)


   .. method:: EncKeyLength(self)



.. function:: YieldStart(builder)


.. function:: YieldAddRequest(builder, request)


.. function:: YieldAddPayload(builder, payload)


.. function:: YieldStartPayloadVector(builder, numElems)


.. function:: YieldAddEncAlgo(builder, encAlgo)


.. function:: YieldAddEncSerializer(builder, encSerializer)


.. function:: YieldAddEncKey(builder, encKey)


.. function:: YieldStartEncKeyVector(builder, numElems)


.. function:: YieldEnd(builder)


