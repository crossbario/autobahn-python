:mod:`autobahn.wamp.gen.wamp.proto.Call`
========================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Call


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Call.Call



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Call.CallStart
   autobahn.wamp.gen.wamp.proto.Call.CallAddRequest
   autobahn.wamp.gen.wamp.proto.Call.CallAddProcedure
   autobahn.wamp.gen.wamp.proto.Call.CallAddPayload
   autobahn.wamp.gen.wamp.proto.Call.CallStartPayloadVector
   autobahn.wamp.gen.wamp.proto.Call.CallAddEncAlgo
   autobahn.wamp.gen.wamp.proto.Call.CallAddEncSerializer
   autobahn.wamp.gen.wamp.proto.Call.CallAddEncKey
   autobahn.wamp.gen.wamp.proto.Call.CallStartEncKeyVector
   autobahn.wamp.gen.wamp.proto.Call.CallAddTimeout
   autobahn.wamp.gen.wamp.proto.Call.CallAddReceiveProgress
   autobahn.wamp.gen.wamp.proto.Call.CallEnd


.. class:: Call

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsCall(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Request(self)


   .. method:: Procedure(self)


   .. method:: Payload(self, j)


   .. method:: PayloadAsNumpy(self)


   .. method:: PayloadLength(self)


   .. method:: EncAlgo(self)


   .. method:: EncSerializer(self)


   .. method:: EncKey(self, j)


   .. method:: EncKeyAsNumpy(self)


   .. method:: EncKeyLength(self)


   .. method:: Timeout(self)


   .. method:: ReceiveProgress(self)



.. function:: CallStart(builder)


.. function:: CallAddRequest(builder, request)


.. function:: CallAddProcedure(builder, procedure)


.. function:: CallAddPayload(builder, payload)


.. function:: CallStartPayloadVector(builder, numElems)


.. function:: CallAddEncAlgo(builder, encAlgo)


.. function:: CallAddEncSerializer(builder, encSerializer)


.. function:: CallAddEncKey(builder, encKey)


.. function:: CallStartEncKeyVector(builder, numElems)


.. function:: CallAddTimeout(builder, timeout)


.. function:: CallAddReceiveProgress(builder, receiveProgress)


.. function:: CallEnd(builder)


