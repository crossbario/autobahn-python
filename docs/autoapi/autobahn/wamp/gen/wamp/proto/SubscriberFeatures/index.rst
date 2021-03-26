:mod:`autobahn.wamp.gen.wamp.proto.SubscriberFeatures`
======================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.SubscriberFeatures


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.SubscriberFeatures.SubscriberFeatures



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.SubscriberFeatures.SubscriberFeaturesStart
   autobahn.wamp.gen.wamp.proto.SubscriberFeatures.SubscriberFeaturesAddPublisherIdentification
   autobahn.wamp.gen.wamp.proto.SubscriberFeatures.SubscriberFeaturesAddPatternBasedSubscription
   autobahn.wamp.gen.wamp.proto.SubscriberFeatures.SubscriberFeaturesAddPublicationTrustlevels
   autobahn.wamp.gen.wamp.proto.SubscriberFeatures.SubscriberFeaturesAddSubscriptionRevocation
   autobahn.wamp.gen.wamp.proto.SubscriberFeatures.SubscriberFeaturesAddEventHistory
   autobahn.wamp.gen.wamp.proto.SubscriberFeatures.SubscriberFeaturesAddAcknowledgeSubscriberReceived
   autobahn.wamp.gen.wamp.proto.SubscriberFeatures.SubscriberFeaturesAddPayloadTransparency
   autobahn.wamp.gen.wamp.proto.SubscriberFeatures.SubscriberFeaturesAddPayloadEncryptionCryptobox
   autobahn.wamp.gen.wamp.proto.SubscriberFeatures.SubscriberFeaturesEnd


.. class:: SubscriberFeatures

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsSubscriberFeatures(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: PublisherIdentification(self)


   .. method:: PatternBasedSubscription(self)


   .. method:: PublicationTrustlevels(self)


   .. method:: SubscriptionRevocation(self)


   .. method:: EventHistory(self)


   .. method:: AcknowledgeSubscriberReceived(self)


   .. method:: PayloadTransparency(self)


   .. method:: PayloadEncryptionCryptobox(self)



.. function:: SubscriberFeaturesStart(builder)


.. function:: SubscriberFeaturesAddPublisherIdentification(builder, publisherIdentification)


.. function:: SubscriberFeaturesAddPatternBasedSubscription(builder, patternBasedSubscription)


.. function:: SubscriberFeaturesAddPublicationTrustlevels(builder, publicationTrustlevels)


.. function:: SubscriberFeaturesAddSubscriptionRevocation(builder, subscriptionRevocation)


.. function:: SubscriberFeaturesAddEventHistory(builder, eventHistory)


.. function:: SubscriberFeaturesAddAcknowledgeSubscriberReceived(builder, acknowledgeSubscriberReceived)


.. function:: SubscriberFeaturesAddPayloadTransparency(builder, payloadTransparency)


.. function:: SubscriberFeaturesAddPayloadEncryptionCryptobox(builder, payloadEncryptionCryptobox)


.. function:: SubscriberFeaturesEnd(builder)


