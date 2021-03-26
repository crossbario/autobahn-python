:mod:`autobahn.wamp.protocol`
=============================

.. py:module:: autobahn.wamp.protocol


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.protocol.BaseSession
   autobahn.wamp.protocol.ApplicationSession
   autobahn.wamp.protocol._SessionShim
   autobahn.wamp.protocol.ApplicationSessionFactory



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.protocol.is_method_or_function


.. function:: is_method_or_function(f)


.. class:: BaseSession


   Bases: :class:`autobahn.util.ObservableMixin`

   WAMP session base class.

   This class implements :class:`autobahn.wamp.interfaces.ISession`.

   .. attribute:: log
      

      

   .. method:: realm(self)
      :property:


   .. method:: session_id(self)
      :property:


   .. method:: authid(self)
      :property:


   .. method:: authrole(self)
      :property:


   .. method:: authmethod(self)
      :property:


   .. method:: authprovider(self)
      :property:


   .. method:: define(self, exception, error=None)

      Implements :func:`autobahn.wamp.interfaces.ISession.define`


   .. method:: _message_from_exception(self, request_type, request, exc, tb=None, enc_algo=None)

      Create a WAMP error message from an exception.

      :param request_type: The request type this WAMP error message is for.
      :type request_type: int

      :param request: The request ID this WAMP error message is for.
      :type request: int

      :param exc: The exception.
      :type exc: Instance of :class:`Exception` or subclass thereof.

      :param tb: Optional traceback. If present, it'll be included with the WAMP error message.
      :type tb: list or None


   .. method:: _exception_from_message(self, msg)

      Create a user (or generic) exception from a WAMP error message.

      :param msg: A WAMP error message.
      :type msg: instance of :class:`autobahn.wamp.message.Error`



.. class:: ApplicationSession(config=None)


   Bases: :class:`autobahn.wamp.protocol.BaseSession`

   WAMP endpoint session.

   .. method:: set_payload_codec(self, payload_codec)

      Implements :func:`autobahn.wamp.interfaces.ISession.set_payload_codec`


   .. method:: get_payload_codec(self)

      Implements :func:`autobahn.wamp.interfaces.ISession.get_payload_codec`


   .. method:: onOpen(self, transport)

      Implements :func:`autobahn.wamp.interfaces.ITransportHandler.onOpen`


   .. method:: onConnect(self)

      Implements :func:`autobahn.wamp.interfaces.ISession.onConnect`


   .. method:: join(self, realm, authmethods=None, authid=None, authrole=None, authextra=None, resumable=None, resume_session=None, resume_token=None)

      Implements :func:`autobahn.wamp.interfaces.ISession.join`


   .. method:: disconnect(self)

      Implements :func:`autobahn.wamp.interfaces.ISession.disconnect`


   .. method:: is_connected(self)

      Implements :func:`autobahn.wamp.interfaces.ISession.is_connected`


   .. method:: is_attached(self)

      Implements :func:`autobahn.wamp.interfaces.ISession.is_attached`


   .. method:: onUserError(self, fail, msg)

      Implements :func:`autobahn.wamp.interfaces.ISession.onUserError`


   .. method:: _swallow_error(self, fail, msg)

      This is an internal generic error-handler for errors encountered
      when calling down to on*() handlers that can reasonably be
      expected to be overridden in user code.

      Note that it *cancels* the error, so use with care!

      Specifically, this should *never* be added to the errback
      chain for a Deferred/coroutine that will make it out to user
      code.


   .. method:: type_check(self, func)

      Does parameter type checking and validation against type hints
      and appropriately tells the user code and the caller (through router).


   .. method:: onMessage(self, msg)

      Implements :func:`autobahn.wamp.interfaces.ITransportHandler.onMessage`


   .. method:: onClose(self, wasClean)

      Implements :func:`autobahn.wamp.interfaces.ITransportHandler.onClose`


   .. method:: onChallenge(self, challenge)

      Implements :func:`autobahn.wamp.interfaces.ISession.onChallenge`


   .. method:: onJoin(self, details)

      Implements :meth:`autobahn.wamp.interfaces.ISession.onJoin`


   .. method:: onWelcome(self, msg)

      Implements :meth:`autobahn.wamp.interfaces.ISession.onWelcome`


   .. method:: _errback_outstanding_requests(self, exc)

      Errback any still outstanding requests with exc.


   .. method:: onLeave(self, details)

      Implements :meth:`autobahn.wamp.interfaces.ISession.onLeave`


   .. method:: leave(self, reason=None, message=None)

      Implements :meth:`autobahn.wamp.interfaces.ISession.leave`


   .. method:: onDisconnect(self)

      Implements :meth:`autobahn.wamp.interfaces.ISession.onDisconnect`


   .. method:: publish(self, topic, *args, **kwargs)

      Implements :meth:`autobahn.wamp.interfaces.IPublisher.publish`


   .. method:: subscribe(self, handler, topic=None, options=None, check_types=False)

      Implements :meth:`autobahn.wamp.interfaces.ISubscriber.subscribe`


   .. method:: _unsubscribe(self, subscription)

      Called from :meth:`autobahn.wamp.protocol.Subscription.unsubscribe`


   .. method:: call(self, procedure, *args, **kwargs)

      Implements :meth:`autobahn.wamp.interfaces.ICaller.call`


   .. method:: register(self, endpoint, procedure=None, options=None, prefix=None, check_types=False)

      Implements :meth:`autobahn.wamp.interfaces.ICallee.register`


   .. method:: _unregister(self, registration)

      Called from :meth:`autobahn.wamp.protocol.Registration.unregister`



.. class:: _SessionShim(config=None)


   Bases: :class:`autobahn.wamp.protocol.ApplicationSession`

   shim that lets us present pep8 API for user-classes to override,
   but also backwards-compatible for existing code using
   ApplicationSession "directly".

   **NOTE:** this is not public or intended for use; you should import
   either autobahn.asyncio.wamp.Session or
   autobahn.twisted.wamp.Session depending on which async
   framework yo're using.

   .. attribute:: _authenticators
      

      

   .. method:: onJoin(self, details)

      Implements :meth:`autobahn.wamp.interfaces.ISession.onJoin`


   .. method:: onConnect(self)

      Implements :func:`autobahn.wamp.interfaces.ISession.onConnect`


   .. method:: onChallenge(self, challenge)

      Implements :func:`autobahn.wamp.interfaces.ISession.onChallenge`


   .. method:: onWelcome(self, msg)

      Implements :meth:`autobahn.wamp.interfaces.ISession.onWelcome`


   .. method:: onLeave(self, details)

      Implements :meth:`autobahn.wamp.interfaces.ISession.onLeave`


   .. method:: onDisconnect(self)

      Implements :meth:`autobahn.wamp.interfaces.ISession.onDisconnect`


   .. method:: add_authenticator(self, authenticator)


   .. method:: _merged_authextra(self)

      internal helper

      :returns: a single 'authextra' dict, consisting of all keys
          from any authenticator's authextra.

      Note that when the authenticator was added, we already checked
      that any keys it does contain has the same value as any
      existing authextra.


   .. method:: on_join(self, details)


   .. method:: on_leave(self, details)


   .. method:: on_connect(self)


   .. method:: on_disconnect(self)



.. class:: ApplicationSessionFactory(config=None)


   Bases: :class:`object`

   WAMP endpoint session factory.

   .. attribute:: session
      

      WAMP application session class to be used in this factory.


   .. method:: __call__(self)

      Creates a new WAMP application session.

      :returns: -- An instance of the WAMP application session class as
                   given by `self.session`.



