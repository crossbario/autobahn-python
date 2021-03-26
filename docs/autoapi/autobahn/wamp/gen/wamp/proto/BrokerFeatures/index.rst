:mod:`autobahn.wamp.gen.wamp.proto.BrokerFeatures`
==================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.BrokerFeatures


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeatures



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesStart
   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesAddPublisherIdentification
   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesAddPublisherExclusion
   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesAddSubscriberBlackwhiteListing
   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesAddPatternBasedSubscription
   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesAddPublicationTrustlevels
   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesAddSubscriptionRevocation
   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesAddSessionMetaApi
   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesAddSubscriptionMetaApi
   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesAddEventRetention
   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesAddEventHistory
   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesAddAcknowledgeEventReceived
   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesAddAcknowledgeSubscriberReceived
   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesAddPayloadTransparency
   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesAddPayloadEncryptionCryptobox
   autobahn.wamp.gen.wamp.proto.BrokerFeatures.BrokerFeaturesEnd


.. class:: BrokerFeatures

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsBrokerFeatures(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: PublisherIdentification(self)


   .. method:: PublisherExclusion(self)


   .. method:: SubscriberBlackwhiteListing(self)


   .. method:: PatternBasedSubscription(self)


   .. method:: PublicationTrustlevels(self)


   .. method:: SubscriptionRevocation(self)


   .. method:: SessionMetaApi(self)


   .. method:: SubscriptionMetaApi(self)


   .. method:: EventRetention(self)


   .. method:: EventHistory(self)


   .. method:: AcknowledgeEventReceived(self)


   .. method:: AcknowledgeSubscriberReceived(self)


   .. method:: PayloadTransparency(self)


   .. method:: PayloadEncryptionCryptobox(self)



.. function:: BrokerFeaturesStart(builder)


.. function:: BrokerFeaturesAddPublisherIdentification(builder, publisherIdentification)


.. function:: BrokerFeaturesAddPublisherExclusion(builder, publisherExclusion)


.. function:: BrokerFeaturesAddSubscriberBlackwhiteListing(builder, subscriberBlackwhiteListing)


.. function:: BrokerFeaturesAddPatternBasedSubscription(builder, patternBasedSubscription)


.. function:: BrokerFeaturesAddPublicationTrustlevels(builder, publicationTrustlevels)


.. function:: BrokerFeaturesAddSubscriptionRevocation(builder, subscriptionRevocation)


.. function:: BrokerFeaturesAddSessionMetaApi(builder, sessionMetaApi)


.. function:: BrokerFeaturesAddSubscriptionMetaApi(builder, subscriptionMetaApi)


.. function:: BrokerFeaturesAddEventRetention(builder, eventRetention)


.. function:: BrokerFeaturesAddEventHistory(builder, eventHistory)


.. function:: BrokerFeaturesAddAcknowledgeEventReceived(builder, acknowledgeEventReceived)


.. function:: BrokerFeaturesAddAcknowledgeSubscriberReceived(builder, acknowledgeSubscriberReceived)


.. function:: BrokerFeaturesAddPayloadTransparency(builder, payloadTransparency)


.. function:: BrokerFeaturesAddPayloadEncryptionCryptobox(builder, payloadEncryptionCryptobox)


.. function:: BrokerFeaturesEnd(builder)


