:mod:`autobahn.wamp.gen.wamp.proto.CallerFeatures`
==================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.CallerFeatures


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.CallerFeatures.CallerFeatures



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.CallerFeatures.CallerFeaturesStart
   autobahn.wamp.gen.wamp.proto.CallerFeatures.CallerFeaturesAddCallerIdentification
   autobahn.wamp.gen.wamp.proto.CallerFeatures.CallerFeaturesAddCallTimeout
   autobahn.wamp.gen.wamp.proto.CallerFeatures.CallerFeaturesAddCallCanceling
   autobahn.wamp.gen.wamp.proto.CallerFeatures.CallerFeaturesAddProgressiveCallResults
   autobahn.wamp.gen.wamp.proto.CallerFeatures.CallerFeaturesAddPayloadTransparency
   autobahn.wamp.gen.wamp.proto.CallerFeatures.CallerFeaturesAddPayloadEncryptionCryptobox
   autobahn.wamp.gen.wamp.proto.CallerFeatures.CallerFeaturesEnd


.. class:: CallerFeatures

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsCallerFeatures(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: CallerIdentification(self)


   .. method:: CallTimeout(self)


   .. method:: CallCanceling(self)


   .. method:: ProgressiveCallResults(self)


   .. method:: PayloadTransparency(self)


   .. method:: PayloadEncryptionCryptobox(self)



.. function:: CallerFeaturesStart(builder)


.. function:: CallerFeaturesAddCallerIdentification(builder, callerIdentification)


.. function:: CallerFeaturesAddCallTimeout(builder, callTimeout)


.. function:: CallerFeaturesAddCallCanceling(builder, callCanceling)


.. function:: CallerFeaturesAddProgressiveCallResults(builder, progressiveCallResults)


.. function:: CallerFeaturesAddPayloadTransparency(builder, payloadTransparency)


.. function:: CallerFeaturesAddPayloadEncryptionCryptobox(builder, payloadEncryptionCryptobox)


.. function:: CallerFeaturesEnd(builder)


