:mod:`autobahn.wamp.gen.wamp.proto.Publish`
===========================================

.. py:module:: autobahn.wamp.gen.wamp.proto.Publish


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Publish.Publish



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.Publish.PublishStart
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddRequest
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddTopic
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddArgs
   autobahn.wamp.gen.wamp.proto.Publish.PublishStartArgsVector
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddKwargs
   autobahn.wamp.gen.wamp.proto.Publish.PublishStartKwargsVector
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddPayload
   autobahn.wamp.gen.wamp.proto.Publish.PublishStartPayloadVector
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddEncAlgo
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddEncSerializer
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddEncKey
   autobahn.wamp.gen.wamp.proto.Publish.PublishStartEncKeyVector
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddAcknowledge
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddExcludeMe
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddExclude
   autobahn.wamp.gen.wamp.proto.Publish.PublishStartExcludeVector
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddExcludeAuthid
   autobahn.wamp.gen.wamp.proto.Publish.PublishStartExcludeAuthidVector
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddExcludeAuthrole
   autobahn.wamp.gen.wamp.proto.Publish.PublishStartExcludeAuthroleVector
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddEligible
   autobahn.wamp.gen.wamp.proto.Publish.PublishStartEligibleVector
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddEligibleAuthid
   autobahn.wamp.gen.wamp.proto.Publish.PublishStartEligibleAuthidVector
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddEligibleAuthrole
   autobahn.wamp.gen.wamp.proto.Publish.PublishStartEligibleAuthroleVector
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddRetain
   autobahn.wamp.gen.wamp.proto.Publish.PublishAddForwardFor
   autobahn.wamp.gen.wamp.proto.Publish.PublishStartForwardForVector
   autobahn.wamp.gen.wamp.proto.Publish.PublishEnd


.. class:: Publish

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsPublish(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: Request(self)


   .. method:: Topic(self)


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


   .. method:: Acknowledge(self)


   .. method:: ExcludeMe(self)


   .. method:: Exclude(self, j)


   .. method:: ExcludeAsNumpy(self)


   .. method:: ExcludeLength(self)


   .. method:: ExcludeAuthid(self, j)


   .. method:: ExcludeAuthidLength(self)


   .. method:: ExcludeAuthrole(self, j)


   .. method:: ExcludeAuthroleLength(self)


   .. method:: Eligible(self, j)


   .. method:: EligibleAsNumpy(self)


   .. method:: EligibleLength(self)


   .. method:: EligibleAuthid(self, j)


   .. method:: EligibleAuthidLength(self)


   .. method:: EligibleAuthrole(self, j)


   .. method:: EligibleAuthroleLength(self)


   .. method:: Retain(self)


   .. method:: ForwardFor(self, j)


   .. method:: ForwardForLength(self)



.. function:: PublishStart(builder)


.. function:: PublishAddRequest(builder, request)


.. function:: PublishAddTopic(builder, topic)


.. function:: PublishAddArgs(builder, args)


.. function:: PublishStartArgsVector(builder, numElems)


.. function:: PublishAddKwargs(builder, kwargs)


.. function:: PublishStartKwargsVector(builder, numElems)


.. function:: PublishAddPayload(builder, payload)


.. function:: PublishStartPayloadVector(builder, numElems)


.. function:: PublishAddEncAlgo(builder, encAlgo)


.. function:: PublishAddEncSerializer(builder, encSerializer)


.. function:: PublishAddEncKey(builder, encKey)


.. function:: PublishStartEncKeyVector(builder, numElems)


.. function:: PublishAddAcknowledge(builder, acknowledge)


.. function:: PublishAddExcludeMe(builder, excludeMe)


.. function:: PublishAddExclude(builder, exclude)


.. function:: PublishStartExcludeVector(builder, numElems)


.. function:: PublishAddExcludeAuthid(builder, excludeAuthid)


.. function:: PublishStartExcludeAuthidVector(builder, numElems)


.. function:: PublishAddExcludeAuthrole(builder, excludeAuthrole)


.. function:: PublishStartExcludeAuthroleVector(builder, numElems)


.. function:: PublishAddEligible(builder, eligible)


.. function:: PublishStartEligibleVector(builder, numElems)


.. function:: PublishAddEligibleAuthid(builder, eligibleAuthid)


.. function:: PublishStartEligibleAuthidVector(builder, numElems)


.. function:: PublishAddEligibleAuthrole(builder, eligibleAuthrole)


.. function:: PublishStartEligibleAuthroleVector(builder, numElems)


.. function:: PublishAddRetain(builder, retain)


.. function:: PublishAddForwardFor(builder, forwardFor)


.. function:: PublishStartForwardForVector(builder, numElems)


.. function:: PublishEnd(builder)


