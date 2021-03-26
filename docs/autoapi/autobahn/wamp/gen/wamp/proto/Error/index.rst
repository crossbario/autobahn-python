:mod:`autobahn.wamp.gen.wamp.proto.Error`
=========================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Error


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Error.Error



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Error.ErrorStart
   autobahn.wamp.gen.wamp.proto.Error.ErrorAddRequestType
   autobahn.wamp.gen.wamp.proto.Error.ErrorAddRequest
   autobahn.wamp.gen.wamp.proto.Error.ErrorAddError
   autobahn.wamp.gen.wamp.proto.Error.ErrorAddPayload
   autobahn.wamp.gen.wamp.proto.Error.ErrorStartPayloadVector
   autobahn.wamp.gen.wamp.proto.Error.ErrorAddEncAlgo
   autobahn.wamp.gen.wamp.proto.Error.ErrorAddEncSerializer
   autobahn.wamp.gen.wamp.proto.Error.ErrorAddEncKey
   autobahn.wamp.gen.wamp.proto.Error.ErrorStartEncKeyVector
   autobahn.wamp.gen.wamp.proto.Error.ErrorEnd


.. class:: Error

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsError(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: RequestType(self)


   .. method:: Request(self)


   .. method:: Error(self)


   .. method:: Payload(self, j)


   .. method:: PayloadAsNumpy(self)


   .. method:: PayloadLength(self)


   .. method:: EncAlgo(self)


   .. method:: EncSerializer(self)


   .. method:: EncKey(self, j)


   .. method:: EncKeyAsNumpy(self)


   .. method:: EncKeyLength(self)



.. function:: ErrorStart(builder)


.. function:: ErrorAddRequestType(builder, requestType)


.. function:: ErrorAddRequest(builder, request)


.. function:: ErrorAddError(builder, error)


.. function:: ErrorAddPayload(builder, payload)


.. function:: ErrorStartPayloadVector(builder, numElems)


.. function:: ErrorAddEncAlgo(builder, encAlgo)


.. function:: ErrorAddEncSerializer(builder, encSerializer)


.. function:: ErrorAddEncKey(builder, encKey)


.. function:: ErrorStartEncKeyVector(builder, numElems)


.. function:: ErrorEnd(builder)


