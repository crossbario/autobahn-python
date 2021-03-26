:mod:`autobahn.wamp.gen.wamp.proto.Invocation`
==============================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Invocation


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Invocation.Invocation



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Invocation.InvocationStart
   autobahn.wamp.gen.wamp.proto.Invocation.InvocationAddRequest
   autobahn.wamp.gen.wamp.proto.Invocation.InvocationAddRegistration
   autobahn.wamp.gen.wamp.proto.Invocation.InvocationAddPayload
   autobahn.wamp.gen.wamp.proto.Invocation.InvocationStartPayloadVector
   autobahn.wamp.gen.wamp.proto.Invocation.InvocationAddEncAlgo
   autobahn.wamp.gen.wamp.proto.Invocation.InvocationAddEncSerializer
   autobahn.wamp.gen.wamp.proto.Invocation.InvocationAddEncKey
   autobahn.wamp.gen.wamp.proto.Invocation.InvocationStartEncKeyVector
   autobahn.wamp.gen.wamp.proto.Invocation.InvocationAddProcedure
   autobahn.wamp.gen.wamp.proto.Invocation.InvocationAddTimeout
   autobahn.wamp.gen.wamp.proto.Invocation.InvocationAddReceiveProgress
   autobahn.wamp.gen.wamp.proto.Invocation.InvocationAddCaller
   autobahn.wamp.gen.wamp.proto.Invocation.InvocationAddCallerAuthid
   autobahn.wamp.gen.wamp.proto.Invocation.InvocationAddCallerAuthrole
   autobahn.wamp.gen.wamp.proto.Invocation.InvocationEnd


.. class:: Invocation

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsInvocation(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Request(self)


   .. method:: Registration(self)


   .. method:: Payload(self, j)


   .. method:: PayloadAsNumpy(self)


   .. method:: PayloadLength(self)


   .. method:: EncAlgo(self)


   .. method:: EncSerializer(self)


   .. method:: EncKey(self, j)


   .. method:: EncKeyAsNumpy(self)


   .. method:: EncKeyLength(self)


   .. method:: Procedure(self)


   .. method:: Timeout(self)


   .. method:: ReceiveProgress(self)


   .. method:: Caller(self)


   .. method:: CallerAuthid(self)


   .. method:: CallerAuthrole(self)



.. function:: InvocationStart(builder)


.. function:: InvocationAddRequest(builder, request)


.. function:: InvocationAddRegistration(builder, registration)


.. function:: InvocationAddPayload(builder, payload)


.. function:: InvocationStartPayloadVector(builder, numElems)


.. function:: InvocationAddEncAlgo(builder, encAlgo)


.. function:: InvocationAddEncSerializer(builder, encSerializer)


.. function:: InvocationAddEncKey(builder, encKey)


.. function:: InvocationStartEncKeyVector(builder, numElems)


.. function:: InvocationAddProcedure(builder, procedure)


.. function:: InvocationAddTimeout(builder, timeout)


.. function:: InvocationAddReceiveProgress(builder, receiveProgress)


.. function:: InvocationAddCaller(builder, caller)


.. function:: InvocationAddCallerAuthid(builder, callerAuthid)


.. function:: InvocationAddCallerAuthrole(builder, callerAuthrole)


.. function:: InvocationEnd(builder)


