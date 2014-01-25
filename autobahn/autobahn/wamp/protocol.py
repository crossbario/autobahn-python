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

from twisted.internet.defer import Deferred, maybeDeferred

from autobahn.wamp.interfaces import IAppSession, \
                                     IPublisher, \
                                     ISubscriber, \
                                     ICaller, \
                                     ICallee, \
                                     IMessageTransportHandler

from autobahn import util
from autobahn import wamp
from autobahn.wamp import message
from autobahn.wamp import types
from autobahn.wamp import role
from autobahn.wamp import exception
from autobahn.wamp.exception import ProtocolError
from autobahn.wamp.types import SessionDetails
from autobahn.wamp.broker import Broker
from autobahn.wamp.dealer import Dealer


@implementer(IAppSession)
class WampBaseSession:

   def __init__(self):
      self._ecls_to_uri_pat = {}
      self._uri_to_ecls = {}


   def define(self, exception, error = None):
      """
      Implements :func:`autobahn.wamp.interfaces.IAppSession.define`
      """
      if error is None:
         assert(hasattr(exception, '_wampuris'))
         self._ecls_to_uri_pat[exception] = exception._wampuris
         self._uri_to_ecls[exception._wampuris[0].uri()] = exception
      else:
         assert(not hasattr(exception, '_wampuris'))
         self._ecls_to_uri_pat[exception] = [Pattern(error, Pattern.URI_TARGET_HANDLER)]
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
         msg = message.Error(request_type, request, exc.args[0], args = exc.args[1:], kwargs = exc.kwargs)
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
@implementer(IMessageTransportHandler)
class WampAppSession(WampBaseSession):

   def __init__(self, broker = None, dealer = None):
      WampBaseSession.__init__(self)
      self._transport = None

      self._broker = broker
      self._dealer = dealer

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
      Implements :func:`autobahn.wamp.interfaces.IMessageTransportHandler.onOpen`
      """
      self._transport = transport

      self._my_session_id = util.id()
      self._peer_session_id = None

      roles = [
         role.RolePublisherFeatures(),
         role.RoleSubscriberFeatures(),
         role.RoleCallerFeatures(),
         role.RoleCalleeFeatures()
      ]

      if self._broker:
         roles.append(role.RoleBrokerFeatures())

      if self._dealer:
         roles.append(role.RoleDealerFeatures())

      msg = message.Hello(self._my_session_id, roles)
      self._transport.send(msg)


   def onMessage(self, msg):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessageTransportHandler.onMessage`
      """
      print "***"*10, msg

      if self._peer_session_id is None:

         ## the first message MUST be HELLO
         if isinstance(msg, message.Hello):
            self._peer_session_id = msg.session

            if self._broker:
               self._broker.addSession(self)

            if self._dealer:
               self._dealer.addSession(self)

            self.onSessionOpen(SessionDetails(self._my_session_id, self._peer_session_id))
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
            self.onSessionClose(msg.reason, msg.message)

            if self._broker:
               self._broker.removeSession(self)

            if self._dealer:
               self._dealer.removeSession(self)

            self._my_session_id = None
            self._peer_session_id = None

            self._transport.close()

         ## broker messages
         ##
         elif isinstance(msg, message.Subscribe):
            if self._broker:
               self._broker.onSubscribe(self, msg)
            else:
               raise ProtocolError("Unexpected message {}".format(msg.__class__))

         elif isinstance(msg, message.Unsubscribe):
            if self._broker:
               self._broker.onUnsubscribe(self, msg)
            else:
               raise ProtocolError("Unexpected message {}".format(msg.__class__))

         elif isinstance(msg, message.Publish):
            if self._broker:
               self._broker.onPublish(self, msg)
            else:
               raise ProtocolError("Unexpected message {}".format(msg.__class__))

         ## dealer messages
         ##
         elif isinstance(msg, message.Register):
            if self._dealer:
               self._dealer.onRegister(self, msg)
            else:
               raise ProtocolError("Unexpected message {}".format(msg.__class__))

         elif isinstance(msg, message.Unregister):
            if self._dealer:
               self._dealer.onUnregister(self, msg)
            else:
               raise ProtocolError("Unexpected message {}".format(msg.__class__))

         elif isinstance(msg, message.Call):
            if self._dealer:
               self._dealer.onCall(self, msg)
            else:
               raise ProtocolError("Unexpected message {}".format(msg.__class__))

         elif isinstance(msg, message.Cancel):
            if self._dealer:
               self._dealer.onCancel(self, msg)
            else:
               raise ProtocolError("Unexpected message {}".format(msg.__class__))

         elif isinstance(msg, message.Yield):
            if self._dealer:
               self._dealer.onYield(self, msg)
            else:
               raise ProtocolError("Unexpected message {}".format(msg.__class__))

         ## consumer messages
         ##
         elif isinstance(msg, message.Event):

            if msg.subscription in self._subscriptions:
               handler = self._subscriptions[msg.subscription]
               try:
                  if msg.kwargs:
                     if msg.args:
                        handler(*msg.args, **msg.kwargs)
                     else:
                        handler(**msg.kwargs)
                  else:
                     if msg.args:
                        handler(*msg.args)
                     else:
                        handler()
               except Exception as e:
                  print("Exception raised in event handler: {}".format(e))
            else:
               raise ProtocolError("EVENT received for non-subscribed subscription ID {}".format(msg.subscription))

         elif isinstance(msg, message.Published):

            if msg.request in self._publish_reqs:
               d = self._publish_reqs.pop(msg.request)
               d.callback(msg.publication)
            else:
               raise ProtocolError("PUBLISHED received for non-pending request ID {}".format(msg.request))

         elif isinstance(msg, message.Subscribed):

            if msg.request in self._subscribe_reqs:
               d, handler = self._subscribe_reqs.pop(msg.request)
               self._subscriptions[msg.subscription] = handler
               d.callback(msg.subscription)
            else:
               raise ProtocolError("SUBSCRIBED received for non-pending request ID {}".format(msg.request))

         elif isinstance(msg, message.Unsubscribed):

            if msg.request in self._unsubscribe_reqs:
               d, subscription = self._unsubscribe_reqs.pop(msg.request)
               if subscription in self._subscriptions:
                  del self._subscriptions[subscription]
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
                        print e
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

                  if endpoint.details:
                     if not msg.kwargs:
                        msg.kwargs = {}
                     if endpoint.details:
                        if msg.receive_progress:
                           def progress(*args, **kwargs):
                              progress_msg = message.Yield(msg.request, args = args, kwargs = kwargs, progress = True)
                              self._transport.send(progress_msg)
                        else:
                           progress = None
                        msg.kwargs[endpoint.details] = types.CallDetails(progress)

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
                  print "X"*100, e
               finally:
                  del self._invocations[msg.request]

         elif isinstance(msg, message.Registered):

            if msg.request in self._register_reqs:
               d, fn, options = self._register_reqs.pop(msg.request)
               self._registrations[msg.registration] = Endpoint(fn, options.details)
               d.callback(msg.registration)
            else:
               raise ProtocolError("REGISTERED received for non-pending request ID {}".format(msg.request))

         elif isinstance(msg, message.Unregistered):

            if msg.request in self._unregister_reqs:
               d, registration = self._unregister_reqs.pop(msg.request)
               if registration in self._registrations:
                  del self._registrations[registration]
               d.callback(None)
            else:
               raise ProtocolError("UNREGISTERED received for non-pending request ID {}".format(msg.request))

         elif isinstance(msg, message.Error):

            if msg.request_type == message.Invocation.MESSAGE_TYPE:

               if self._dealer:
                  self._dealer.onInvocationError(self, msg)
               else:
                  raise ProtocolError("Unexpected message {}".format(msg.__class__))

            else:

               d = None

               ## ERROR reply to PUBLISH
               ##
               if msg.request_type == message.Publish.MESSAGE_TYPE and msg.request in self._publish_reqs:
                  d = self._publish_reqs.pop(msg.request)

               elif msg.request_type == message.Subscribe.MESSAGE_TYPE and msg.request in self._subscribe_reqs:
                  d, _ = self._subscribe_reqs.pop(msg.request)

               elif msg.request_type == message.Unsubscribe.MESSAGE_TYPE and msg.request in self._unsubscribe_reqs:
                  d = self._unsubscribe_reqs.pop(msg.request)

               elif msg.request_type == message.Call.MESSAGE_TYPE and msg.request in self._call_reqs:
                  d, _ = self._call_reqs.pop(msg.request)

               if d:
                  d.errback(self._exception_from_message(msg))
               else:
                  raise ProtocolError("WampAppSession.onMessage(): ERROR received for non-pending request_type {} and request ID {}".format(msg.request_type, msg.request))

         elif isinstance(msg, message.Heartbeat):

            pass ## FIXME

         else:

            raise ProtocolError("Unexpected message {}".format(msg.__class__))


   def onClose(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessageTransportHandler.onClose`
      """
      self._transport = None

      if self._my_session_id:

         ## fire callback and close the transport
         try:
            self.onSessionClose(None, None)
         except Exception as e:
            print e

         if self._broker:
            self._broker.removeSession(self)

         if self._dealer:
            self._dealer.removeSession(self)

         self._my_session_id = None
         self._peer_session_id = None


   def closeSession(self, reason = None, message = None):
      """
      Implements :func:`autobahn.wamp.interfaces.IAppSession.closeSession`
      """
      if not self._goodbye_sent:
         msg = wamp.message.Goodbye(reason = reason, message = message)
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

      d = Deferred()
      self._publish_reqs[request] = d

      if 'options' in kwargs and isinstance(kwargs['options'], wamp.options.Publish):
         opts = kwargs.pop('options')
         msg = message.Publish(request, topic, args = args, kwargs = kwargs, **opts.__dict__)
      else:
         msg = message.Publish(request, topic, args = args, kwargs = kwargs)

      self._transport.send(msg)
      return d


   def subscribe(self, handler, topic = None, options = None):
      """
      Implements :func:`autobahn.wamp.interfaces.ISubscriber.subscribe`
      """
      assert(callable(handler))
      assert(type(topic) in (str, unicode))
      assert(options is None or isinstance(options, wamp.options.Subscribe))

      if not self._transport:
         raise exception.TransportLost()

      request = util.id()

      d = Deferred()
      self._subscribe_reqs[request] = (d, handler)

      if options is not None:
         msg = message.Subscribe(request, topic, **options.__dict__)
      else:
         msg = message.Subscribe(request, topic)

      self._transport.send(msg)
      return d


   def unsubscribe(self, subscription):
      """
      Implements :func:`autobahn.wamp.interfaces.ISubscriber.unsubscribe`
      """
      assert(type(subscription) in [int, long])
      assert(subscription in self._subscriptions)

      if not self._transport:
         raise exception.TransportLost()

      request = util.id()

      d = Deferred()
      self._unsubscribe_reqs[request] = (d, subscription)

      msg = message.Unsubscribe(request, subscription)

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


   def unregister(self, registration):
      """
      Implements :func:`autobahn.wamp.interfaces.ICallee.unregister`
      """
      assert(type(registration) in [int, long])
      assert(registration in self._registrations)

      if not self._transport:
         raise exception.TransportLost()

      request = util.id()

      d = Deferred()
      self._unregister_reqs[request] = (d, registration)

      msg = message.Unregister(request, registration)

      self._transport.send(msg)
      return d



class WampAppFactory:

   def __call__(self):
      session = self.session()
      session.factory = self
      return session


import inspect

def get_class_default_arg(fn, klass):
   argspec = inspect.getargspec(fn)
   print klass, fn, argspec
   if argspec.defaults:
      for i in range(len(argspec.defaults)):
         print argspec.defaults[-i]
         if argspec.defaults[-i] == klass:
            return argspec.args[-i]
   return None


class Endpoint:

   def __init__(self, fn, details):
      self.fn = fn
      self.details = details
      #self.details_arg = get_class_default_arg(fn, types.CallDetails)




class WampRouterAppSession:

   def __init__(self, session, broker, dealer):
      self._broker = broker
      self._dealer = dealer

      self._session = session
      self._session._transport = self
      self._session._my_session_id = util.id()
      self._session._peer_session_id = util.id()
      self._broker.addSession(self._session)
      self._dealer.addSession(self._session)
      self._session.onSessionOpen(SessionDetails(self._session._my_session_id, self._session._peer_session_id))

   def send(self, msg):
      print "WampRouterAppSession.send", msg

      ## app-to-broker
      ##
      if isinstance(msg, message.Publish):
         self._broker.onPublish(self._session, msg)
      elif isinstance(msg, message.Subscribe):
         self._broker.onSubscribe(self._session, msg)
      elif isinstance(msg, message.Unsubscribe):
         self._broker.onUnsubscribe(self._session, msg)

      ## app-to-dealer
      ##
      elif isinstance(msg, message.Register):
         self._dealer.onRegister(self._session, msg)
      elif isinstance(msg, message.Unregister):
         self._dealer.onUnregister(self._session, msg)
      elif isinstance(msg, message.Call):
         self._dealer.onCall(self._session, msg)
      elif isinstance(msg, message.Cancel):
         self._dealer.onCancel(self._session, msg)
      elif isinstance(msg, message.Yield):
         self._dealer.onYield(self._session, msg)
      elif isinstance(msg, message.Error) and msg.request_type == message.Invocation.MESSAGE_TYPE:
         self._dealer.onInvocationError(self._session, msg)

      ## broker/dealer-to-app
      ##
      elif isinstance(msg, message.Event) or \
           isinstance(msg, message.Subscribed) or \
           isinstance(msg, message.Unsubscribed) or \
           isinstance(msg, message.Result) or \
           isinstance(msg, message.Invocation) or \
           isinstance(msg, message.Registered) or \
           isinstance(msg, message.Unregistered):
         try:
            self._session.onMessage(msg)
         except Exception as e:
            print "X"*10, e

      else:
         raise Exception("WampRouterAppSession.send: unhandled message {}".format(msg))



class WampRouterSession(WampAppSession):

   def onSessionOpen(self, info):
      print "WampRouterSession.onSessionOpen", info.me, info.peer

   def onSessionClose(self, reason, message):
      print "WampRouterSession.onSessionOpen", reason, message



class WampRouterFactory:

   def __init__(self):
      self._broker = Broker()
      self._dealer = Dealer()
      self._app_sessions = []

   def add(self, app_session):
      self._app_sessions.append(WampRouterAppSession(app_session, self._broker, self._dealer))

   def __call__(self):
      return WampRouterSession(self._broker, self._dealer)
