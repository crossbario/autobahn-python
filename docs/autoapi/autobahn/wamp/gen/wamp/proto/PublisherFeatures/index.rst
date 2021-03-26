:mod:`autobahn.wamp.gen.wamp.proto.PublisherFeatures`
=====================================================

.. py:module:: autobahn.wamp.gen.wamp.proto.PublisherFeatures


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.PublisherFeatures.PublisherFeatures



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.gen.wamp.proto.PublisherFeatures.PublisherFeaturesStart
   autobahn.wamp.gen.wamp.proto.PublisherFeatures.PublisherFeaturesAddPublisherIdentification
   autobahn.wamp.gen.wamp.proto.PublisherFeatures.PublisherFeaturesAddPublisherExclusion
   autobahn.wamp.gen.wamp.proto.PublisherFeatures.PublisherFeaturesAddSubscriberBlackwhiteListing
   autobahn.wamp.gen.wamp.proto.PublisherFeatures.PublisherFeaturesAddAcknowledgeEventReceived
   autobahn.wamp.gen.wamp.proto.PublisherFeatures.PublisherFeaturesAddPayloadTransparency
   autobahn.wamp.gen.wamp.proto.PublisherFeatures.PublisherFeaturesAddPayloadEncryptionCryptobox
   autobahn.wamp.gen.wamp.proto.PublisherFeatures.PublisherFeaturesEnd


.. class:: PublisherFeatures

   Bases: :class:`object`

   .. attribute:: __slots__
      :annotation: = ['_tab']

      

   .. method:: GetRootAsPublisherFeatures(cls, buf, offset)
      :classmethod:


   .. method:: Init(self, buf, pos)


   .. method:: PublisherIdentification(self)


   .. method:: PublisherExclusion(self)


   .. method:: SubscriberBlackwhiteListing(self)


   .. method:: AcknowledgeEventReceived(self)


   .. method:: PayloadTransparency(self)


   .. method:: PayloadEncryptionCryptobox(self)



.. function:: PublisherFeaturesStart(builder)


.. function:: PublisherFeaturesAddPublisherIdentification(builder, publisherIdentification)


.. function:: PublisherFeaturesAddPublisherExclusion(builder, publisherExclusion)


.. function:: PublisherFeaturesAddSubscriberBlackwhiteListing(builder, subscriberBlackwhiteListing)


.. function:: PublisherFeaturesAddAcknowledgeEventReceived(builder, acknowledgeEventReceived)


.. function:: PublisherFeaturesAddPayloadTransparency(builder, payloadTransparency)


.. function:: PublisherFeaturesAddPayloadEncryptionCryptobox(builder, payloadEncryptionCryptobox)


.. function:: PublisherFeaturesEnd(builder)


