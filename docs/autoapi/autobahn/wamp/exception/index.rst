:mod:`autobahn.wamp.exception`
==============================

.. py:module:: autobahn.wamp.exception


Module Contents
---------------

.. exception:: Error


   Bases: :class:`RuntimeError`

   Base class for all exceptions related to WAMP.


.. exception:: SessionNotReady


   Bases: :class:`autobahn.wamp.exception.Error`

   The application tried to perform a WAMP interaction, but the
   session is not yet fully established.


.. exception:: SerializationError


   Bases: :class:`autobahn.wamp.exception.Error`

   Exception raised when the WAMP serializer could not serialize the
   application payload (``args`` or ``kwargs`` for ``CALL``, ``PUBLISH``, etc).


.. exception:: ProtocolError


   Bases: :class:`autobahn.wamp.exception.Error`

   Exception raised when WAMP protocol was violated. Protocol errors
   are fatal and are handled by the WAMP implementation. They are
   not supposed to be handled at the application level.


.. exception:: TransportLost


   Bases: :class:`autobahn.wamp.exception.Error`

   Exception raised when the transport underlying the WAMP session
   was lost or is not connected.


.. exception:: ApplicationError(error, *args, **kwargs)


   Bases: :class:`autobahn.wamp.exception.Error`

   Base class for all exceptions that can/may be handled
   at the application level.

   .. attribute:: INVALID_URI
      :annotation: = wamp.error.invalid_uri

      Peer provided an incorrect URI for a URI-based attribute of a WAMP message
      such as a realm, topic or procedure.


   .. attribute:: INVALID_PAYLOAD
      :annotation: = wamp.error.invalid_payload

      The application payload could not be serialized.


   .. attribute:: PAYLOAD_SIZE_EXCEEDED
      :annotation: = wamp.error.payload_size_exceeded

      The application payload could not be transported becuase the serialized/framed payload
      exceeds the transport limits.


   .. attribute:: NO_SUCH_PROCEDURE
      :annotation: = wamp.error.no_such_procedure

      A Dealer could not perform a call, since not procedure is currently registered
      under the given URI.


   .. attribute:: PROCEDURE_ALREADY_EXISTS
      :annotation: = wamp.error.procedure_already_exists

      A procedure could not be registered, since a procedure with the given URI is
      already registered.


   .. attribute:: PROCEDURE_EXISTS_INVOCATION_POLICY_CONFLICT
      :annotation: = wamp.error.procedure_exists_with_different_invocation_policy

      A procedure could not be registered, since a procedure with the given URI is
      already registered, and the registration has a conflicting invocation policy.


   .. attribute:: NO_SUCH_REGISTRATION
      :annotation: = wamp.error.no_such_registration

      A Dealer could not perform a unregister, since the given registration is not active.


   .. attribute:: NO_SUCH_SUBSCRIPTION
      :annotation: = wamp.error.no_such_subscription

      A Broker could not perform a unsubscribe, since the given subscription is not active.


   .. attribute:: NO_SUCH_SESSION
      :annotation: = wamp.error.no_such_session

      A router could not perform an operation, since a session ID specified was non-existant.


   .. attribute:: INVALID_ARGUMENT
      :annotation: = wamp.error.invalid_argument

      A call failed, since the given argument types or values are not acceptable to the
      called procedure - in which case the *Callee* may throw this error. Or a Router
      performing *payload validation* checked the payload (``args`` / ``kwargs``) of a call,
      call result, call error or publish, and the payload did not conform.


   .. attribute:: SYSTEM_SHUTDOWN
      :annotation: = wamp.error.system_shutdown

      The *Peer* is shutting down completely - used as a ``GOODBYE`` (or ``ABORT``) reason.


   .. attribute:: CLOSE_REALM
      :annotation: = wamp.error.close_realm

      The *Peer* want to leave the realm - used as a ``GOODBYE`` reason.


   .. attribute:: GOODBYE_AND_OUT
      :annotation: = wamp.error.goodbye_and_out

      A *Peer* acknowledges ending of a session - used as a ``GOOBYE`` reply reason.


   .. attribute:: NOT_AUTHORIZED
      :annotation: = wamp.error.not_authorized

      A call, register, publish or subscribe failed, since the session is not authorized
      to perform the operation.


   .. attribute:: AUTHORIZATION_FAILED
      :annotation: = wamp.error.authorization_failed

      A Dealer or Broker could not determine if the *Peer* is authorized to perform
      a join, call, register, publish or subscribe, since the authorization operation
      *itself* failed. E.g. a custom authorizer did run into an error.


   .. attribute:: AUTHENTICATION_FAILED
      :annotation: = wamp.error.authentication_failed

      Something failed with the authentication itself, that is, authentication could
      not run to end.


   .. attribute:: NO_AUTH_METHOD
      :annotation: = wamp.error.no_auth_method

      No authentication method the peer offered is available or active.


   .. attribute:: NO_SUCH_REALM
      :annotation: = wamp.error.no_such_realm

      Peer wanted to join a non-existing realm (and the *Router* did not allow to auto-create
      the realm).


   .. attribute:: NO_SUCH_ROLE
      :annotation: = wamp.error.no_such_role

      A *Peer* was to be authenticated under a Role that does not (or no longer) exists on the Router.
      For example, the *Peer* was successfully authenticated, but the Role configured does not
      exists - hence there is some misconfiguration in the Router.


   .. attribute:: NO_SUCH_PRINCIPAL
      :annotation: = wamp.error.no_such_principal

      A *Peer* was authenticated for an authid that does not or longer exists.


   .. attribute:: CANCELED
      :annotation: = wamp.error.canceled

      A Dealer or Callee canceled a call previously issued (WAMP AP).


   .. attribute:: TIMEOUT
      :annotation: = wamp.error.timeout

      A pending (in-flight) call was timed out.


   .. attribute:: NO_ELIGIBLE_CALLEE
      :annotation: = wamp.error.no_eligible_callee

      A *Dealer* could not perform a call, since a procedure with the given URI is registered,
      but *Callee Black- and Whitelisting* and/or *Caller Exclusion* lead to the
      exclusion of (any) *Callee* providing the procedure (WAMP AP).


   .. attribute:: ENC_NO_PAYLOAD_CODEC
      :annotation: = wamp.error.no_payload_codec

      WAMP message in payload transparency mode received, but no codec set
      or codec did not decode the payload.


   .. attribute:: ENC_TRUSTED_URI_MISMATCH
      :annotation: = wamp.error.encryption.trusted_uri_mismatch

      WAMP-cryptobox application payload end-to-end encryption error.


   .. attribute:: ENC_DECRYPT_ERROR
      :annotation: = wamp.error.encryption.decrypt_error

      WAMP-cryptobox application payload end-to-end encryption error.


   .. attribute:: TYPE_CHECK_ERROR
      :annotation: = wamp.error.type_check_error

      WAMP procedure called with wrong argument types or subscription published
      with wrong argument types.


   .. method:: error_message(self)

      Get the error message of this exception.

      :returns: The error message.
      :rtype: str


   .. method:: __unicode__(self)


   .. method:: __str__(self)

      Return str(self).



.. exception:: NotAuthorized


   Bases: :class:`Exception`

   Not authorized to perform the respective action.


.. exception:: InvalidUri


   Bases: :class:`Exception`

   The URI for a topic, procedure or error is not a valid WAMP URI.


