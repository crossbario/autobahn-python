:mod:`autobahn.wamp.gen.wamp.proto.Result`
==========================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Result


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Result.Result



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Result.ResultStart
   autobahn.wamp.gen.wamp.proto.Result.ResultAddRequest
   autobahn.wamp.gen.wamp.proto.Result.ResultAddPayload
   autobahn.wamp.gen.wamp.proto.Result.ResultStartPayloadVector
   autobahn.wamp.gen.wamp.proto.Result.ResultAddEncAlgo
   autobahn.wamp.gen.wamp.proto.Result.ResultAddEncSerializer
   autobahn.wamp.gen.wamp.proto.Result.ResultAddEncKey
   autobahn.wamp.gen.wamp.proto.Result.ResultStartEncKeyVector
   autobahn.wamp.gen.wamp.proto.Result.ResultAddProgress
   autobahn.wamp.gen.wamp.proto.Result.ResultEnd


.. class:: Result

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsResult(cls, buf, offset)
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


   .. method:: Progress(self)



.. function:: ResultStart(builder)


.. function:: ResultAddRequest(builder, request)


.. function:: ResultAddPayload(builder, payload)


.. function:: ResultStartPayloadVector(builder, numElems)


.. function:: ResultAddEncAlgo(builder, encAlgo)


.. function:: ResultAddEncSerializer(builder, encSerializer)


.. function:: ResultAddEncKey(builder, encKey)


.. function:: ResultStartEncKeyVector(builder, numElems)


.. function:: ResultAddProgress(builder, progress)


.. function:: ResultEnd(builder)


