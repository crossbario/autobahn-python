:mod:`autobahn.wamp.gen.wamp.proto.DealerFeatures`
==================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.DealerFeatures


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeatures



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeaturesStart
   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeaturesAddCallerIdentification
   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeaturesAddCallTrustlevels
   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeaturesAddCallTimeout
   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeaturesAddCallCanceling
   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeaturesAddProgressiveCallResults
   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeaturesAddRegistrationRevocation
   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeaturesAddPatternBasedRegistration
   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeaturesAddSharedRegistration
   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeaturesAddSessionMetaApi
   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeaturesAddRegistrationMetaApi
   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeaturesAddTestamentMetaApi
   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeaturesAddPayloadTransparency
   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeaturesAddPayloadEncryptionCryptobox
   autobahn.wamp.gen.wamp.proto.DealerFeatures.DealerFeaturesEnd


.. class:: DealerFeatures

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsDealerFeatures(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: CallerIdentification(self)


   .. method:: CallTrustlevels(self)


   .. method:: CallTimeout(self)


   .. method:: CallCanceling(self)


   .. method:: ProgressiveCallResults(self)


   .. method:: RegistrationRevocation(self)


   .. method:: PatternBasedRegistration(self)


   .. method:: SharedRegistration(self)


   .. method:: SessionMetaApi(self)


   .. method:: RegistrationMetaApi(self)


   .. method:: TestamentMetaApi(self)


   .. method:: PayloadTransparency(self)


   .. method:: PayloadEncryptionCryptobox(self)



.. function:: DealerFeaturesStart(builder)


.. function:: DealerFeaturesAddCallerIdentification(builder, callerIdentification)


.. function:: DealerFeaturesAddCallTrustlevels(builder, callTrustlevels)


.. function:: DealerFeaturesAddCallTimeout(builder, callTimeout)


.. function:: DealerFeaturesAddCallCanceling(builder, callCanceling)


.. function:: DealerFeaturesAddProgressiveCallResults(builder, progressiveCallResults)


.. function:: DealerFeaturesAddRegistrationRevocation(builder, registrationRevocation)


.. function:: DealerFeaturesAddPatternBasedRegistration(builder, patternBasedRegistration)


.. function:: DealerFeaturesAddSharedRegistration(builder, sharedRegistration)


.. function:: DealerFeaturesAddSessionMetaApi(builder, sessionMetaApi)


.. function:: DealerFeaturesAddRegistrationMetaApi(builder, registrationMetaApi)


.. function:: DealerFeaturesAddTestamentMetaApi(builder, testamentMetaApi)


.. function:: DealerFeaturesAddPayloadTransparency(builder, payloadTransparency)


.. function:: DealerFeaturesAddPayloadEncryptionCryptobox(builder, payloadEncryptionCryptobox)


.. function:: DealerFeaturesEnd(builder)


