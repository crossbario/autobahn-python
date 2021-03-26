:mod:`autobahn.wamp.gen.wamp.proto.CalleeFeatures`
==================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.CalleeFeatures


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.CalleeFeatures.CalleeFeatures



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.CalleeFeatures.CalleeFeaturesStart
   autobahn.wamp.gen.wamp.proto.CalleeFeatures.CalleeFeaturesAddCallerIdentification
   autobahn.wamp.gen.wamp.proto.CalleeFeatures.CalleeFeaturesAddCallTrustlevels
   autobahn.wamp.gen.wamp.proto.CalleeFeatures.CalleeFeaturesAddCallTimeout
   autobahn.wamp.gen.wamp.proto.CalleeFeatures.CalleeFeaturesAddCallCanceling
   autobahn.wamp.gen.wamp.proto.CalleeFeatures.CalleeFeaturesAddProgressiveCallResults
   autobahn.wamp.gen.wamp.proto.CalleeFeatures.CalleeFeaturesAddRegistrationRevocation
   autobahn.wamp.gen.wamp.proto.CalleeFeatures.CalleeFeaturesAddPatternBasedRegistration
   autobahn.wamp.gen.wamp.proto.CalleeFeatures.CalleeFeaturesAddSharedRegistration
   autobahn.wamp.gen.wamp.proto.CalleeFeatures.CalleeFeaturesAddPayloadTransparency
   autobahn.wamp.gen.wamp.proto.CalleeFeatures.CalleeFeaturesAddPayloadEncryptionCryptobox
   autobahn.wamp.gen.wamp.proto.CalleeFeatures.CalleeFeaturesEnd


.. class:: CalleeFeatures

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsCalleeFeatures(cls, buf, offset)
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


   .. method:: PayloadTransparency(self)


   .. method:: PayloadEncryptionCryptobox(self)



.. function:: CalleeFeaturesStart(builder)


.. function:: CalleeFeaturesAddCallerIdentification(builder, callerIdentification)


.. function:: CalleeFeaturesAddCallTrustlevels(builder, callTrustlevels)


.. function:: CalleeFeaturesAddCallTimeout(builder, callTimeout)


.. function:: CalleeFeaturesAddCallCanceling(builder, callCanceling)


.. function:: CalleeFeaturesAddProgressiveCallResults(builder, progressiveCallResults)


.. function:: CalleeFeaturesAddRegistrationRevocation(builder, registrationRevocation)


.. function:: CalleeFeaturesAddPatternBasedRegistration(builder, patternBasedRegistration)


.. function:: CalleeFeaturesAddSharedRegistration(builder, sharedRegistration)


.. function:: CalleeFeaturesAddPayloadTransparency(builder, payloadTransparency)


.. function:: CalleeFeaturesAddPayloadEncryptionCryptobox(builder, payloadEncryptionCryptobox)


.. function:: CalleeFeaturesEnd(builder)


