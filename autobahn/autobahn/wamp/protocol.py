###############################################################################
##
##  Copyright (C) 2013-2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

from __future__ import absolute_import

from zope.interface import implementer

from twisted.python import log
from twisted.internet.defer import Deferred, maybeDeferred

from autobahn.wamp.interfaces import ISession, \
                                     IPublication, \
                                     IPublisher, \
                                     ISubscription, \
                                     ISubscriber, \
                                     ICaller, \
                                     IRegistration, \
                                     ICallee, \
                                     ITransportHandler

from autobahn import util
from autobahn import wamp
from autobahn.wamp import uri
from autobahn.wamp import message
from autobahn.wamp import types
from autobahn.wamp import role
from autobahn.wamp import exception
from autobahn.wamp.exception import ProtocolError, SessionNotReady
from autobahn.wamp.types import SessionDetails



class Endpoint:
   """
   """

   def __init__(self, fn, details_arg = None):
      self.fn = fn
      self.details_arg = details_arg



class Handler:
   """
   """

   def __init__(self, fn, details_arg = None):
      self.fn = fn
      self.details_arg = details_arg



@implementer(IPublication)
class Publication:
   """
   Object representing a publication.
   This class implements :class:`autobahn.wamp.interfaces.IPublication`.
   """
   def __init__(self, publicationId):
      self.id = publicationId



@implementer(ISubscription)
class Subscription:
   """
   Object representing a subscription.
   This class implements :class:`autobahn.wamp.interfaces.ISubscription`.
   """
   def __init__(self, session, subscriptionId):
      self._session = session
      self.active = True
      self.id = subscriptionId

   def unsubscribe(self):
      """
      Implements :func:`autobahn.wamp.interfaces.ISubscription.unsubscribe`
      """
      return self._session._unsubscribe(self)



@implementer(IRegistration)
class Registration:
   """
   Object representing a registration.
   This class implements :class:`autobahn.wamp.interfaces.IRegistration`.
   """
   def __init__(self, session, registrationId):
      self._session = session
      self.active = True
      self.id = registrationId

   def unregister(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IRegistration.unregister`
      """
      return self._session._unregister(self)



@implementer(ISession)
class BaseSession:
   """
   WAMP session base class.

   This class implements:

     * :class:`autobahn.wamp.interfaces.ISession`
   """

   def __init__(self):
      """
      Ctor.
      """
      self.debug = False
      self._ecls_to_uri_pat = {}
      self._uri_to_ecls = {}


   def onConnect(self):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.onConnect`
      """


   def onJoin(self, details):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.onJoin`
      """


   def onLeave(self, details):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.onLeave`
      """


   def onDisconnect(self):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.onDisconnect`
      """


   def define(self, exception, error = None):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.define`
      """
      if error is None:
         assert(hasattr(exception, '_wampuris'))
         self._ecls_to_uri_pat[exception] = exception._wampuris
         self._uri_to_ecls[exception._wampuris[0].uri()] = exception
      else:
         assert(not hasattr(exception, '_wampuris'))
         self._ecls_to_uri_pat[exception] = [uri.Pattern(error, uri.Pattern.URI_TARGET_HANDLER)]
         self._uri_to_ecls[error] = exception


   def _message_from_exception(self, request_type, request, exc):
      """
      Create a WAMP error message from an exception.

      :param request: The request ID this WAMP error message is for.
      :type request: int
      :param exc: The exception.
      :type exc: Instance of :class:`Exception` or subclass thereof.
      """
      if isinstance(exc, exception.ApplicationError):
         msg = message.Error(request_type, request, exc.error, args = list(exc.args), kwargs = exc.kwargs)
      else:
         if self._ecls_to_uri_pat.has_key(exc.__class__):
            error = self._ecls_to_uri_pat[exc.__class__][0]._uri
         else:
            error = "wamp.error.runtime_error"

         if hasattr(exc, 'args'):
            if hasattr(exc, 'kwargs'):
               msg = message.Error(request_type, request, error, args = exc.args, kwargs = exc.kwargs)
            else:
               msg = message.Error(request_type, request, error, args = exc.args)
         else:
            msg = message.Error(request_type, request, error)

      return msg


   def _exception_from_message(self, msg):
      """
      Create a user (or generic) exception from a WAMP error message.

      :param msg: A WAMP error message.
      :type msg: Instance of :class:`autobahn.wamp.message.Error`
      """

      # FIXME:
      # 1. map to ecls based on error URI wildcard/prefix
      # 2. extract additional args/kwargs from error URI

      exc = None

      if self._uri_to_ecls.has_key(msg.error):
         ecls = self._uri_to_ecls[msg.error]
         try:
            ## the following might fail, eg. TypeError when
            ## signature of exception constructor is incompatible
            ## with args/kwargs or when the exception constructor raises
            if msg.kwargs:
               if msg.args:
                  exc = ecls(*msg.args, **msg.kwargs)
               else:
                  exc = ecls(**msg.kwargs)
            else:
               if msg.args:
                  exc = ecls(*msg.args)
               else:
                  exc = ecls()
         except Exception as e:
            ## FIXME: log e
            pass

      if not exc:
         ## the following ctor never fails ..
         if msg.kwargs:
            if msg.args:
               exc = exception.ApplicationError(msg.error, *msg.args, **msg.kwargs)
            else:
               exc = exception.ApplicationError(msg.error, **msg.kwargs)
         else:
            if msg.args:
               exc = exception.ApplicationError(msg.error, *msg.args)
            else:
               exc = exception.ApplicationError(msg.error)

      return exc



@implementer(IPublisher)
@implementer(ISubscriber)
@implementer(ICaller)
@implementer(ICallee)
@implementer(ITransportHandler)
class ApplicationSession(BaseSession):
   """
   WAMP endpoint session.

   This class implements:

     * :class:`autobahn.wamp.interfaces.IPublisher`
     * :class:`autobahn.wamp.interfaces.ISubscriber`
     * :class:`autobahn.wamp.interfaces.ICaller`
     * :class:`autobahn.wamp.interfaces.ICallee`
     * :class:`autobahn.wamp.interfaces.ITransportHandler`
   """
   realm = "anonymous"

   def __init__(self):
      """
      Constructor.
      """
      BaseSession.__init__(self)
      self._transport = None

      self._session_id = None
      self._goodbye_sent = False
      self._transport_is_closing = False

      ## outstanding requests
      self._publish_reqs = {}
      self._subscribe_reqs = {}
      self._unsubscribe_reqs = {}
      self._call_reqs = {}
      self._register_reqs = {}
      self._unregister_reqs = {}

      ## subscriptions in place
      self._subscriptions = {}

      ## registrations in place
      self._registrations = {}

      ## incoming invocations
      self._invocations = {}


   def onOpen(self, transport):
      """
      Implements :func:`autobahn.wamp.interfaces.ITransportHandler.onOpen`
      """
      self._transport = transport
      self._session_id = None
      self.onConnect()


   def join(self, realm):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.join`
      """
      if self._session_id:
         raise Exception("already joined")

      self._goodbye_sent = False

      roles = [
         role.RolePublisherFeatures(),
         role.RoleSubscriberFeatures(),
         role.RoleCallerFeatures(),
         role.RoleCalleeFeatures()
      ]

      msg = message.Hello(realm, roles)
      self._transport.send(msg)


   def disconnect(self):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.disconnect`
      """
      if self._transport:
         self._transport.close()
      else:
         raise Exception("transport disconnected")


   def onMessage(self, msg):
      """
      Implements :func:`autobahn.wamp.interfaces.ITransportHandler.onMessage`
      """
      if self._session_id is None:

         ## the first message MUST be WELCOME
         if isinstance(msg, message.Welcome):
            self._session_id = msg.session

            self.onJoin(SessionDetails(self._session_id))
         else:
            raise ProtocolError("Received {} message, and session is not yet established".format(msg.__class__))

      else:

         if isinstance(msg, message.Goodbye):
            if not self._goodbye_sent:
               ## the peer wants to close: send GOODBYE reply
               reply = message.Goodbye()
               self._transport.send(reply)

            self._session_id = None

            ## fire callback and close the transport
            self.onLeave(types.CloseDetails(msg.reason, msg.message))

         ## consumer messages
         ##
         elif isinstance(msg, message.Event):

            if msg.subscription in self._subscriptions:

               handler = self._subscriptions[msg.subscription]

               if handler.details_arg:
                  if not msg.kwargs:
                     msg.kwargs = {}
                  msg.kwargs[handler.details_arg] = types.EventDetails(publication = msg.publication, publisher = msg.publisher)

               try:
                  if msg.kwargs:
                     if msg.args:
                        handler.fn(*msg.args, **msg.kwargs)
                     else:
                        handler.fn(**msg.kwargs)
                  else:
                     if msg.args:
                        handler.fn(*msg.args)
                     else:
                        handler.fn()
               except Exception as e:
                  log.msg("Exception raised in event handler: {}".format(e))

            else:
               raise ProtocolError("EVENT received for non-subscribed subscription ID {}".format(msg.subscription))

         elif isinstance(msg, message.Published):

            if msg.request in self._publish_reqs:
               d, opts = self._publish_reqs.pop(msg.request)
               p = Publication(msg.publication)
               d.callback(p)
            else:
               raise ProtocolError("PUBLISHED received for non-pending request ID {}".format(msg.request))

         elif isinstance(msg, message.Subscribed):

            if msg.request in self._subscribe_reqs:
               d, fn, options = self._subscribe_reqs.pop(msg.request)
               if options:
                  self._subscriptions[msg.subscription] = Handler(fn, options.details_arg)
               else:
                  self._subscriptions[msg.subscription] = Handler(fn)
               s = Subscription(self, msg.subscription)
               d.callback(s)
            else:
               raise ProtocolError("SUBSCRIBED received for non-pending request ID {}".format(msg.request))

         elif isinstance(msg, message.Unsubscribed):

            if msg.request in self._unsubscribe_reqs:
               d, subscription = self._unsubscribe_reqs.pop(msg.request)
               if subscription.id in self._subscriptions:
                  del self._subscriptions[subscription.id]
               subscription.active = False
               d.callback(None)
            else:
               raise ProtocolError("UNSUBSCRIBED received for non-pending request ID {}".format(msg.request))

         elif isinstance(msg, message.Result):

            if msg.request in self._call_reqs:

               if msg.progress:

                  ## progressive result
                  ##
                  _, opts = self._call_reqs[msg.request]
                  if opts.onProgress:
                     try:
                        if msg.kwargs:
                           if msg.args:
                              opts.onProgress(*msg.args, **msg.kwargs)
                           else:
                              opts.onProgress(**msg.kwargs)
                        else:
                           if msg.args:
                              opts.onProgress(*msg.args)
                           else:
                              opts.onProgress()
                     except Exception as e:
                        ## silently drop exceptions raised in progressive results handlers
                        if self.debug:
                           log.msg("Exception raised in progressive results handler: {}".format(e))
                  else:
                     ## silently ignore progressive results
                     pass
               else:

                  ## final result
                  ##
                  d, opts = self._call_reqs.pop(msg.request)
                  if msg.kwargs:
                     if msg.args:
                        res = types.CallResult(*msg.args, **msg.kwargs)
                     else:
                        res = types.CallResult(**msg.kwargs)
                     d.callback(res)
                  else:
                     if msg.args:
                        if len(msg.args) > 1:
                           res = types.CallResult(*msg.args)
                           d.callback(res)
                        else:
                           d.callback(msg.args[0])
                     else:
                        d.callback(None)
            else:
               raise ProtocolError("RESULT received for non-pending request ID {}".format(msg.request))

         elif isinstance(msg, message.Invocation):

            if msg.request in self._invocations:

               raise ProtocolError("INVOCATION received for request ID {} already invoked".format(msg.request))

            else:

               if msg.registration not in self._registrations:

                  raise ProtocolError("INVOCATION received for non-registered registration ID {}".format(msg.registration))

               else:
                  endpoint = self._registrations[msg.registration]

                  if endpoint.details_arg:

                     if not msg.kwargs:
                        msg.kwargs = {}

                     if msg.receive_progress:
                        def progress(*args, **kwargs):
                           progress_msg = message.Yield(msg.request, args = args, kwargs = kwargs, progress = True)
                           self._transport.send(progress_msg)
                     else:
                        progress = None

                     if msg.caller:
                        caller = msg.caller
                     else:
                        caller = None

                     msg.kwargs[endpoint.details_arg] = types.CallDetails(progress, caller = caller)

                  if msg.kwargs:
                     if msg.args:
                        d = maybeDeferred(endpoint.fn, *msg.args, **msg.kwargs)
                     else:
                        d = maybeDeferred(endpoint.fn, **msg.kwargs)
                  else:
                     if msg.args:
                        d = maybeDeferred(endpoint.fn, *msg.args)
                     else:
                        d = maybeDeferred(endpoint.fn)

                  def success(res):
                     del self._invocations[msg.request]

                     if isinstance(res, types.CallResult):
                        reply = message.Yield(msg.request, args = res.results, kwargs = res.kwresults)
                     else:
                        reply = message.Yield(msg.request, args = [res])
                     self._transport.send(reply)

                  def error(err):
                     del self._invocations[msg.request]

                     reply = self._message_from_exception(message.Invocation.MESSAGE_TYPE, msg.request, err.value)
                     self._transport.send(reply)

                  self._invocations[msg.request] = d

                  d.addCallbacks(success, error)

         elif isinstance(msg, message.Interrupt):

            if msg.request not in self._invocations:
               raise ProtocolError("INTERRUPT received for non-pending invocation {}".format(msg.request))
            else:
               try:
                  self._invocations[msg.request].cancel()
               except Exception as e:
                  if self.debug:
                     log.msg("could not cancel call {}".format(msg.request))
               finally:
                  del self._invocations[msg.request]

         elif isinstance(msg, message.Registered):

            if msg.request in self._register_reqs:
               d, fn, options = self._register_reqs.pop(msg.request)
               if options:
                  self._registrations[msg.registration] = Endpoint(fn, options.details_arg)
               else:
                  self._registrations[msg.registration] = Endpoint(fn)
               r = Registration(self, msg.registration)
               d.callback(r)
            else:
               raise ProtocolError("REGISTERED received for non-pending request ID {}".format(msg.request))

         elif isinstance(msg, message.Unregistered):

            if msg.request in self._unregister_reqs:
               d, registration = self._unregister_reqs.pop(msg.request)
               if registration.id in self._registrations:
                  del self._registrations[registration.id]
               registration.active = False
               d.callback(None)
            else:
               raise ProtocolError("UNREGISTERED received for non-pending request ID {}".format(msg.request))

         elif isinstance(msg, message.Error):

            d = None

            ## ERROR reply to PUBLISH
            ##
            if msg.request_type == message.Publish.MESSAGE_TYPE and msg.request in self._publish_reqs:
               d = self._publish_reqs.pop(msg.request)[0]

            ## ERROR reply to SUBSCRIBE
            ##
            elif msg.request_type == message.Subscribe.MESSAGE_TYPE and msg.request in self._subscribe_reqs:
               d = self._subscribe_reqs.pop(msg.request)[0]

            ## ERROR reply to UNSUBSCRIBE
            ##
            elif msg.request_type == message.Unsubscribe.MESSAGE_TYPE and msg.request in self._unsubscribe_reqs:
               d = self._unsubscribe_reqs.pop(msg.request)[0]

            ## ERROR reply to REGISTER
            ##
            elif msg.request_type == message.Register.MESSAGE_TYPE and msg.request in self._register_reqs:
               d = self._register_reqs.pop(msg.request)[0]

            ## ERROR reply to UNREGISTER
            ##
            elif msg.request_type == message.Unregister.MESSAGE_TYPE and msg.request in self._unregister_reqs:
               d = self._unregister_reqs.pop(msg.request)[0]

            ## ERROR reply to CALL
            ##
            elif msg.request_type == message.Call.MESSAGE_TYPE and msg.request in self._call_reqs:
               d = self._call_reqs.pop(msg.request)[0]

            if d:
               d.errback(self._exception_from_message(msg))
            else:
               raise ProtocolError("WampAppSession.onMessage(): ERROR received for non-pending request_type {} and request ID {}".format(msg.request_type, msg.request))

         elif isinstance(msg, message.Heartbeat):

            pass ## FIXME

         else:

            raise ProtocolError("Unexpected message {}".format(msg.__class__))


   def onClose(self, wasClean):
      """
      Implements :func:`autobahn.wamp.interfaces.ITransportHandler.onClose`
      """
      self._transport = None

      if self._session_id:

         ## fire callback and close the transport
         try:
            self.onLeave(types.CloseDetails())
         except Exception as e:
            if self.debug:
               log.msg("exception raised in onLeave callback: {}".format(e))

         self._session_id = None

      self.onDisconnect()


   def onJoin(self, details):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.onJoin`
      """


   def onLeave(self, details):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.onLeave`
      """


   def leave(self, reason = None, log_message = None):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.leave`
      """
      if not self._session_id:
         raise Exception("not joined")

      if not self._goodbye_sent:
         if not reason:
            reason = "wamp.close.normal"
         msg = wamp.message.Goodbye(reason = reason, message = log_message)
         self._transport.send(msg)
         self._goodbye_sent = True
      else:
         raise SessionNotReady("Already requested to close the session")


   def publish(self, topic, *args, **kwargs):
      """
      Implements :func:`autobahn.wamp.interfaces.IPublisher.publish`
      """
      assert(type(topic) in (str, unicode))

      if not self._transport:
         raise exception.TransportLost()

      request = util.id()

      if 'options' in kwargs and isinstance(kwargs['options'], types.PublishOptions):
         opts = kwargs.pop('options')
         msg = message.Publish(request, topic, args = args, kwargs = kwargs, **opts.options)
      else:
         opts = None
         msg = message.Publish(request, topic, args = args, kwargs = kwargs)

      if opts and opts.options['acknowledge'] == True:
         d = Deferred()
         self._publish_reqs[request] = d, opts
         self._transport.send(msg)
         return d
      else:
         self._transport.send(msg)
         return


   def subscribe(self, handler, topic = None, options = None):
      """
      Implements :func:`autobahn.wamp.interfaces.ISubscriber.subscribe`
      """
      assert(callable(handler))
      assert(type(topic) in (str, unicode))
      assert(options is None or isinstance(options, types.SubscribeOptions))

      if not self._transport:
         raise exception.TransportLost()

      request = util.id()

      d = Deferred()
      self._subscribe_reqs[request] = (d, handler, options)

      if options is not None:
         msg = message.Subscribe(request, topic, **options.options)
      else:
         msg = message.Subscribe(request, topic)

      self._transport.send(msg)
      return d


   def _unsubscribe(self, subscription):
      """
      Called from :meth:`autobahn.wamp.protocol.Subscription.unsubscribe`
      """
      assert(isinstance(subscription, Subscription))
      assert(subscription.active)
      assert(subscription.id in self._subscriptions)

      if not self._transport:
         raise exception.TransportLost()

      request = util.id()

      d = Deferred()
      self._unsubscribe_reqs[request] = (d, subscription)

      msg = message.Unsubscribe(request, subscription.id)

      self._transport.send(msg)
      return d


   def call(self, procedure, *args, **kwargs):
      """
      Implements :func:`autobahn.wamp.interfaces.ICaller.call`
      """
      assert(type(procedure) in (str, unicode))

      if not self._transport:
         raise exception.TransportLost()

      request = util.id()

      if 'options' in kwargs and isinstance(kwargs['options'], types.CallOptions):
         opts = kwargs.pop('options')
         msg = message.Call(request, procedure, args = args, kwargs = kwargs, **opts.options)
      else:
         opts = None
         msg = message.Call(request, procedure, args = args, kwargs = kwargs)

      def canceller(_d):
         cancel_msg = message.Cancel(request)
         self._transport.send(cancel_msg)

      d = Deferred(canceller)
      self._call_reqs[request] = d, opts

      self._transport.send(msg)
      return d


   def register(self, endpoint, procedure = None, options = None):
      """
      Implements :func:`autobahn.wamp.interfaces.ICallee.register`
      """
      assert(callable(endpoint))
      assert(type(procedure) in (str, unicode))
      assert(options is None or isinstance(options, types.RegisterOptions))

      if not self._transport:
         raise exception.TransportLost()

      request = util.id()

      d = Deferred()
      self._register_reqs[request] = (d, endpoint, options)

      if options is not None:
         msg = message.Register(request, procedure, **options.options)
      else:
         msg = message.Register(request, procedure)

      self._transport.send(msg)
      return d


   def _unregister(self, registration):
      """
      Called from :meth:`autobahn.wamp.protocol.Registration.unregister`
      """
      assert(isinstance(registration, Registration))
      assert(registration.active)
      assert(registration.id in self._registrations)

      if not self._transport:
         raise exception.TransportLost()

      request = util.id()

      d = Deferred()
      self._unregister_reqs[request] = (d, registration)

      msg = message.Unregister(request, registration.id)

      self._transport.send(msg)
      return d



class ApplicationSessionFactory:
   """
   WAMP endpoint session factory.
   """

   session = ApplicationSession
   """
   WAMP application session class to be used in this factory.
   """

   def __call__(self):
      """
      Creates a new WAMP application session.

      :returns: -- An instance of the WAMP application session class as
                   given by `self.session`.
      """
      session = self.session()
      session.factory = self
      return session



class RouterApplicationSession:
   """
   Wraps an application session to run directly attached to a WAMP router (broker+dealer).
   """

   def __init__(self, session, routerFactory):
      """
      Wrap an application session and add it to the given broker and dealer.

      :param session: Application session to wrap.
      :type session: An instance that implements :class:`autobahn.wamp.interfaces.ISession`
      :param routerFactory: The router factory to associate this session with.
      :type routerFactory: An instance that implements :class:`autobahn.wamp.interfaces.IRouterFactory`
      """

      ## remember router we are wrapping the app session for
      ##
      self._routerFactory = routerFactory
      self._router = None

      ## remember wrapped app session
      ##
      self._session = session

      ## set fake transport on session ("pass-through transport")
      ##
      self._session._transport = self

      self._session.onConnect()


   def isOpen(self):
      """
      Implements :func:`autobahn.wamp.interfaces.ITransport.isOpen`
      """


   def close(self):
      """
      Implements :func:`autobahn.wamp.interfaces.ITransport.close`
      """
      if self._router:
         self._router.detach(self._session)


   def abort(self):
      """
      Implements :func:`autobahn.wamp.interfaces.ITransport.abort`
      """


   def send(self, msg):
      """
      Implements :func:`autobahn.wamp.interfaces.ITransport.send`
      """
      if isinstance(msg, message.Hello):

         self._router = self._routerFactory.get(msg.realm)

         ## fake session ID assignment (normally done in WAMP opening handshake)
         self._session._session_id = util.id()

         ## add app session to router
         self._router.attach(self._session)

         ## fake app session open
         ##
         self._session.onJoin(SessionDetails(self._session._session_id))


      ## app-to-router
      ##
      elif isinstance(msg, message.Publish) or \
           isinstance(msg, message.Subscribe) or \
           isinstance(msg, message.Unsubscribe) or \
           isinstance(msg, message.Call) or \
           isinstance(msg, message.Yield) or \
           isinstance(msg, message.Register) or \
           isinstance(msg, message.Unregister) or \
           isinstance(msg, message.Cancel) or \
          (isinstance(msg, message.Error) and
               msg.request_type == message.Invocation.MESSAGE_TYPE):

         ## deliver message to router
         ##
         self._router.process(self._session, msg)

      ## router-to-app
      ##
      elif isinstance(msg, message.Event) or \
           isinstance(msg, message.Invocation) or \
           isinstance(msg, message.Result) or \
           isinstance(msg, message.Published) or \
           isinstance(msg, message.Subscribed) or \
           isinstance(msg, message.Unsubscribed) or \
           isinstance(msg, message.Registered) or \
           isinstance(msg, message.Unregistered) or \
          (isinstance(msg, message.Error) and (
               msg.request_type == message.Call.MESSAGE_TYPE or
               msg.request_type == message.Cancel.MESSAGE_TYPE or
               msg.request_type == message.Register.MESSAGE_TYPE or
               msg.request_type == message.Unregister.MESSAGE_TYPE or
               msg.request_type == message.Publish.MESSAGE_TYPE or
               msg.request_type == message.Subscribe.MESSAGE_TYPE or
               msg.request_type == message.Unsubscribe.MESSAGE_TYPE)):

         ## deliver message to app session
         ##
         self._session.onMessage(msg)

      else:
         ## should not arrive here
         ##
         raise Exception("RouterApplicationSession.send: unhandled message {}".format(msg))



@implementer(ITransportHandler)
class RouterSession(BaseSession):
   """
   WAMP router session.

   This class implements:

     * :class:`autobahn.wamp.interfaces.ITransportHandler`
   """

   def __init__(self, routerFactory):
      """
      Constructor.
      """
      BaseSession.__init__(self)
      self._transport = None

      self._router_factory = routerFactory
      self._router = None
      self._realm = None

      self._goodbye_sent = False
      self._transport_is_closing = False


   def onOpen(self, transport):
      """
      Implements :func:`autobahn.wamp.interfaces.ITransportHandler.onOpen`
      """
      self._transport = transport
      self._session_id = None


   def onHello(self, realm):
      return True


   def onAuthenticate(self, signature):
      return True


   def onMessage(self, msg):
      """
      Implements :func:`autobahn.wamp.interfaces.ITransportHandler.onMessage`
      """
      if self._session_id is None:

         ## the first message MUST be HELLO
         if isinstance(msg, message.Hello):

            if self.onHello(msg.realm):

               self._session_id = util.id()
               self._goodbye_sent = False

               self._router = self._router_factory.get(msg.realm)
               if not self._router:
                  raise Exception("no such realm")

               roles = self._router.attach(self)
               msg = message.Welcome(self._session_id, roles)
               self._transport.send(msg)

               self.onJoin(SessionDetails(self._session_id))

            else:

               self._realm = msg.realm

               msg = message.Challenge("something")
               self._transport.send(msg)

         elif isinstance(msg, message.Authenticate):

            if self.onAuthenticate(msg.signature):

               self._session_id = util.id()
               self._goodbye_sent = False

               self._router = self._router_factory.get(self._realm)
               if not self._router:
                  raise Exception("no such realm")

               roles = self._router.attach(self)
               msg = message.Welcome(self._session_id, roles)
               self._transport.send(msg)

               self.onJoin(SessionDetails(self._session_id))

         else:
            raise ProtocolError("Received {} message, and session is not yet established".format(msg.__class__))

      else:

         if isinstance(msg, message.Hello):
            raise ProtocolError("HELLO message received, while session is already established")

         elif isinstance(msg, message.Goodbye):
            if not self._goodbye_sent:
               ## the peer wants to close: send GOODBYE reply
               reply = message.Goodbye()
               self._transport.send(reply)

            ## fire callback and close the transport
            self.onLeave(types.CloseDetails(msg.reason, msg.message))

            self._router.detach(self)

            self._session_id = None

            #self._transport.close()

         elif isinstance(msg, message.Heartbeat):

            pass ## FIXME

         else:

            self._router.process(self, msg)


   def onClose(self, wasClean):
      """
      Implements :func:`autobahn.wamp.interfaces.ITransportHandler.onClose`
      """
      self._transport = None

      if self._session_id:

         ## fire callback and close the transport
         try:
            self.onLeave(types.CloseDetails())
         except Exception as e:
            if self.debug:
               log.msg("exception raised in onLeave callback: {}".format(e))

         self._router.detach(self)

         self._session_id = None


   def onJoin(self, details):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.onJoin`
      """


   def onLeave(self, details):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.onLeave`
      """


   def leave(self, reason = None, message = None):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.leave`
      """
      if not self._goodbye_sent:
         msg = wamp.message.Goodbye(reason = reason, message = message)
         self._transport.send(msg)
         self._goodbye_sent = True
      else:
         raise SessionNotReady("Already requested to close the session")



class RouterSessionFactory:
   """
   WAMP router session factory.
   """

   session = RouterSession
   """
   WAMP router session class to be used in this factory.
   """


   def __init__(self, routerFactory):
      """
      Constructor.
      """
      self._routerFactory = routerFactory
      self._app_sessions = {}


   def add(self, session):
      """
      Adds a WAMP application session to run directly in this router.

      :param: session: A WAMP application session.
      :type session: A instance of a class that derives of :class:`autobahn.wamp.protocol.WampAppSession`
      """
      #router = self._routerFactory.get(session.realm)
      self._app_sessions[session] = RouterApplicationSession(session, self._routerFactory)


   def remove(self, session):
      """
      Removes a WAMP application session running directly in this router.
      """
      if session in self._app_sessions:
         self._app_sessions[session]._session.disconnect()
         del self._app_sessions[session]



   def __call__(self):
      """
      Creates a new WAMP router session.

      :returns: -- An instance of the WAMP router session class as
                   given by `self.session`.
      """
      session = self.session(self._routerFactory)
      session.factory = session
      return session
