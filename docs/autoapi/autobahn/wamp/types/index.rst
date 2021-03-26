:mod:`autobahn.wamp.types`
==========================

.. py:module:: autobahn.wamp.types


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.types.ComponentConfig
   autobahn.wamp.types.HelloReturn
   autobahn.wamp.types.Accept
   autobahn.wamp.types.Deny
   autobahn.wamp.types.Challenge
   autobahn.wamp.types.HelloDetails
   autobahn.wamp.types.SessionDetails
   autobahn.wamp.types.SessionIdent
   autobahn.wamp.types.CloseDetails
   autobahn.wamp.types.SubscribeOptions
   autobahn.wamp.types.EventDetails
   autobahn.wamp.types.PublishOptions
   autobahn.wamp.types.RegisterOptions
   autobahn.wamp.types.CallDetails
   autobahn.wamp.types.CallOptions
   autobahn.wamp.types.CallResult
   autobahn.wamp.types.EncodedPayload



.. class:: ComponentConfig(realm=None, extra=None, keyring=None, controller=None, shared=None, runner=None)


   Bases: :class:`object`

   WAMP application component configuration. An instance of this class is
   provided to the constructor of :class:`autobahn.wamp.protocol.ApplicationSession`.

   .. attribute:: __slots__
      :annotation: = ['realm', 'extra', 'keyring', 'controller', 'shared', 'runner']

      

   .. method:: __str__(self)

      Return str(self).



.. class:: HelloReturn

   Bases: :class:`object`

   Base class for ``HELLO`` return information.


.. class:: Accept(realm=None, authid=None, authrole=None, authmethod=None, authprovider=None, authextra=None)


   Bases: :class:`autobahn.wamp.types.HelloReturn`

   Information to accept a ``HELLO``.

   .. attribute:: __slots__
      :annotation: = ['realm', 'authid', 'authrole', 'authmethod', 'authprovider', 'authextra']

      

   .. method:: __str__(self)

      Return str(self).



.. class:: Deny(reason='wamp.error.not_authorized', message=None)


   Bases: :class:`autobahn.wamp.types.HelloReturn`

   Information to deny a ``HELLO``.

   .. attribute:: __slots__
      :annotation: = ['reason', 'message']

      

   .. method:: __str__(self)

      Return str(self).



.. class:: Challenge(method, extra=None)


   Bases: :class:`autobahn.wamp.types.HelloReturn`

   Information to challenge the client upon ``HELLO``.

   .. attribute:: __slots__
      :annotation: = ['method', 'extra']

      

   .. method:: __str__(self)

      Return str(self).



.. class:: HelloDetails(realm=None, authmethods=None, authid=None, authrole=None, authextra=None, session_roles=None, pending_session=None, resumable=None, resume_session=None, resume_token=None)


   Bases: :class:`object`

   Provides details of a WAMP session while still attaching.

   .. attribute:: __slots__
      :annotation: = ['realm', 'authmethods', 'authid', 'authrole', 'authextra', 'session_roles', 'pending_session', 'resumable', 'resume_session', 'resume_token']

      

   .. method:: __str__(self)

      Return str(self).



.. class:: SessionDetails(realm, session, authid=None, authrole=None, authmethod=None, authprovider=None, authextra=None, serializer=None, transport=None, resumed=None, resumable=None, resume_token=None)


   Bases: :class:`object`

   Provides details for a WAMP session upon open.

   .. seealso:: :meth:`autobahn.wamp.interfaces.ISession.onJoin`

   .. attribute:: __slots__
      :annotation: = ['realm', 'session', 'authid', 'authrole', 'authmethod', 'authprovider', 'authextra', 'serializer', 'transport', 'resumed', 'resumable', 'resume_token']

      

   .. method:: marshal(self)


   .. method:: __str__(self)

      Return str(self).



.. class:: SessionIdent(session=None, authid=None, authrole=None)


   Bases: :class:`object`

   WAMP session identification information.

   A WAMP session joined on a realm on a WAMP router is identified technically
   by its session ID (``session``) already.

   The permissions the session has are tied to the WAMP authentication role (``authrole``).

   The subject behind the session, eg the user or the application component is identified
   by the WAMP authentication ID (``authid``). One session is always authenticated under/as
   one specific ``authid``, but a given ``authid`` might have zero, one or many sessions
   joined on a router at the same time.

   .. attribute:: __slots__
      :annotation: = ['session', 'authid', 'authrole']

      

   .. method:: __str__(self)

      Return str(self).


   .. method:: marshal(self)


   .. method:: from_calldetails(call_details)
      :staticmethod:

      Create a new session identification object from the caller information
      in the call details provided.

      :param call_details: Details of a WAMP call.
      :type call_details: :class:`autobahn.wamp.types.CallDetails`

      :returns: New session identification object.
      :rtype: :class:`autobahn.wamp.types.SessionIdent`


   .. method:: from_eventdetails(event_details)
      :staticmethod:

      Create a new session identification object from the publisher information
      in the event details provided.

      :param event_details: Details of a WAMP event.
      :type event_details: :class:`autobahn.wamp.types.EventDetails`

      :returns: New session identification object.
      :rtype: :class:`autobahn.wamp.types.SessionIdent`



.. class:: CloseDetails(reason=None, message=None)


   Bases: :class:`object`

   Provides details for a WAMP session upon close.

   .. seealso:: :meth:`autobahn.wamp.interfaces.ISession.onLeave`

   .. attribute:: REASON_DEFAULT
      :annotation: = wamp.close.normal

      

   .. attribute:: REASON_TRANSPORT_LOST
      :annotation: = wamp.close.transport_lost

      

   .. attribute:: __slots__
      :annotation: = ['reason', 'message']

      

   .. method:: marshal(self)


   .. method:: __str__(self)

      Return str(self).



.. class:: SubscribeOptions(match=None, details=None, details_arg=None, forward_for=None, get_retained=None, correlation_id=None, correlation_uri=None, correlation_is_anchor=None, correlation_is_last=None)


   Bases: :class:`object`

   Used to provide options for subscribing in
   :meth:`autobahn.wamp.interfaces.ISubscriber.subscribe`.

   .. attribute:: __slots__
      :annotation: = ['match', 'details', 'details_arg', 'get_retained', 'forward_for', 'correlation_id', 'correlation_uri', 'correlation_is_anchor', 'correlation_is_last']

      

   .. method:: message_attr(self)

      Returns options dict as sent within WAMP messages.


   .. method:: __str__(self)

      Return str(self).



.. class:: EventDetails(subscription, publication, publisher=None, publisher_authid=None, publisher_authrole=None, topic=None, retained=None, enc_algo=None, forward_for=None)


   Bases: :class:`object`

   Provides details on an event when calling an event handler
   previously registered.

   .. attribute:: __slots__
      :annotation: = ['subscription', 'publication', 'publisher', 'publisher_authid', 'publisher_authrole', 'topic', 'retained', 'enc_algo', 'forward_for']

      

   .. method:: __str__(self)

      Return str(self).



.. class:: PublishOptions(acknowledge=None, exclude_me=None, exclude=None, exclude_authid=None, exclude_authrole=None, eligible=None, eligible_authid=None, eligible_authrole=None, retain=None, forward_for=None, correlation_id=None, correlation_uri=None, correlation_is_anchor=None, correlation_is_last=None)


   Bases: :class:`object`

   Used to provide options for subscribing in
   :meth:`autobahn.wamp.interfaces.IPublisher.publish`.

   .. attribute:: __slots__
      :annotation: = ['acknowledge', 'exclude_me', 'exclude', 'exclude_authid', 'exclude_authrole', 'eligible', 'eligible_authid', 'eligible_authrole', 'retain', 'forward_for', 'correlation_id', 'correlation_uri', 'correlation_is_anchor', 'correlation_is_last']

      

   .. method:: message_attr(self)

      Returns options dict as sent within WAMP messages.


   .. method:: __str__(self)

      Return str(self).



.. class:: RegisterOptions(match=None, invoke=None, concurrency=None, force_reregister=None, forward_for=None, details=None, details_arg=None, correlation_id=None, correlation_uri=None, correlation_is_anchor=None, correlation_is_last=None)


   Bases: :class:`object`

   Used to provide options for registering in
   :meth:`autobahn.wamp.interfaces.ICallee.register`.

   .. attribute:: __slots__
      :annotation: = ['match', 'invoke', 'concurrency', 'force_reregister', 'forward_for', 'details', 'details_arg', 'correlation_id', 'correlation_uri', 'correlation_is_anchor', 'correlation_is_last']

      

   .. method:: message_attr(self)

      Returns options dict as sent within WAMP messages.


   .. method:: __str__(self)

      Return str(self).



.. class:: CallDetails(registration, progress=None, caller=None, caller_authid=None, caller_authrole=None, procedure=None, enc_algo=None, forward_for=None)


   Bases: :class:`object`

   Provides details on a call when an endpoint previously
   registered is being called and opted to receive call details.

   .. attribute:: __slots__
      :annotation: = ['registration', 'progress', 'caller', 'caller_authid', 'caller_authrole', 'procedure', 'enc_algo', 'forward_for']

      

   .. method:: __str__(self)

      Return str(self).



.. class:: CallOptions(on_progress=None, timeout=None, caller=None, caller_authid=None, caller_authrole=None, forward_for=None, correlation_id=None, correlation_uri=None, correlation_is_anchor=None, correlation_is_last=None, details=None)


   Bases: :class:`object`

   Used to provide options for calling with :meth:`autobahn.wamp.interfaces.ICaller.call`.

   .. attribute:: __slots__
      :annotation: = ['on_progress', 'timeout', 'caller', 'caller_authid', 'caller_authrole', 'forward_for', 'correlation_id', 'correlation_uri', 'correlation_is_anchor', 'correlation_is_last', 'details']

      

   .. method:: message_attr(self)

      Returns options dict as sent within WAMP messages.


   .. method:: __str__(self)

      Return str(self).



.. class:: CallResult(*results, **kwresults)


   Bases: :class:`object`

   Wrapper for remote procedure call results that contain multiple positional
   return values or keyword-based return values.

   .. attribute:: __slots__
      :annotation: = ['results', 'kwresults', 'enc_algo', 'callee', 'callee_authid', 'callee_authrole', 'forward_for']

      

   .. method:: __str__(self)

      Return str(self).



.. class:: EncodedPayload(payload, enc_algo, enc_serializer=None, enc_key=None)


   Bases: :class:`object`

   Wrapper holding an encoded application payload when using WAMP payload transparency.

   .. attribute:: __slots__
      :annotation: = ['payload', 'enc_algo', 'enc_serializer', 'enc_key']

      


