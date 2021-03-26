:mod:`autobahn.wamp.role`
=========================

.. py:module:: autobahn.wamp.role


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.role.RoleFeatures
   autobahn.wamp.role.RoleBrokerFeatures
   autobahn.wamp.role.RoleSubscriberFeatures
   autobahn.wamp.role.RolePublisherFeatures
   autobahn.wamp.role.RoleDealerFeatures
   autobahn.wamp.role.RoleCallerFeatures
   autobahn.wamp.role.RoleCalleeFeatures



.. class:: RoleFeatures

   Bases: :class:`autobahn.util.EqualityMixin`

   Base class for WAMP role features.

   .. attribute:: ROLE
      

      

   .. method:: __str__(self)

      Return str(self).


   .. method:: __repr__(self)

      Return repr(self).


   .. method:: _check_all_bool(self)



.. class:: RoleBrokerFeatures(publisher_identification=None, publication_trustlevels=None, pattern_based_subscription=None, session_meta_api=None, subscription_meta_api=None, subscriber_blackwhite_listing=None, publisher_exclusion=None, subscription_revocation=None, event_history=None, payload_transparency=None, x_acknowledged_event_delivery=None, payload_encryption_cryptobox=None, event_retention=None, **kwargs)


   Bases: :class:`autobahn.wamp.role.RoleFeatures`

   WAMP broker role features.

   .. attribute:: ROLE
      :annotation: = broker

      


.. class:: RoleSubscriberFeatures(publisher_identification=None, publication_trustlevels=None, pattern_based_subscription=None, subscription_revocation=None, event_history=None, payload_transparency=None, payload_encryption_cryptobox=None, **kwargs)


   Bases: :class:`autobahn.wamp.role.RoleFeatures`

   WAMP subscriber role features.

   .. attribute:: ROLE
      :annotation: = subscriber

      


.. class:: RolePublisherFeatures(publisher_identification=None, subscriber_blackwhite_listing=None, publisher_exclusion=None, payload_transparency=None, x_acknowledged_event_delivery=None, payload_encryption_cryptobox=None, **kwargs)


   Bases: :class:`autobahn.wamp.role.RoleFeatures`

   WAMP publisher role features.

   .. attribute:: ROLE
      :annotation: = publisher

      


.. class:: RoleDealerFeatures(caller_identification=None, call_trustlevels=None, pattern_based_registration=None, session_meta_api=None, registration_meta_api=None, shared_registration=None, call_timeout=None, call_canceling=None, progressive_call_results=None, registration_revocation=None, payload_transparency=None, testament_meta_api=None, payload_encryption_cryptobox=None, **kwargs)


   Bases: :class:`autobahn.wamp.role.RoleFeatures`

   WAMP dealer role features.

   .. attribute:: ROLE
      :annotation: = dealer

      


.. class:: RoleCallerFeatures(caller_identification=None, call_timeout=None, call_canceling=None, progressive_call_results=None, payload_transparency=None, payload_encryption_cryptobox=None, **kwargs)


   Bases: :class:`autobahn.wamp.role.RoleFeatures`

   WAMP caller role features.

   .. attribute:: ROLE
      :annotation: = caller

      


.. class:: RoleCalleeFeatures(caller_identification=None, call_trustlevels=None, pattern_based_registration=None, shared_registration=None, call_timeout=None, call_canceling=None, progressive_call_results=None, registration_revocation=None, payload_transparency=None, payload_encryption_cryptobox=None, **kwargs)


   Bases: :class:`autobahn.wamp.role.RoleFeatures`

   WAMP callee role features.

   .. attribute:: ROLE
      :annotation: = callee

      


.. data:: ROLE_NAME_TO_CLASS
   

   

.. data:: DEFAULT_CLIENT_ROLES
   

   

