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

from twisted.internet.defer import Deferred, \
                                   maybeDeferred

from autobahn.wamp.interfaces import ISession, \
                                     IPublisher, \
                                     ISubscriber, \
                                     ICaller, \
                                     ICallee, \
                                     IMessageTransportHandler, \
                                     IMessageTransport

from autobahn import wamp
from autobahn.wamp.exception import ProtocolError
from autobahn.wamp import message
from autobahn import util
from autobahn.wamp import serializer
from autobahn.wamp import exception
from autobahn.wamp import types
from autobahn.wamp import options
from autobahn.wamp import role


@implementer(ISession)
class WampBaseSession:

   def __init__(self):
      self._ecls_to_uri_pat = {}
      self._uri_to_ecls = {}


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
         self._ecls_to_uri_pat[exception] = [Pattern(error, Pattern.URI_TARGET_HANDLER)]
         self._uri_to_ecls[error] = exception


   def _message_from_exception(self, request, exc):
      """
      Create a WAMP error message from an exception.

      :param request: The request ID this WAMP error message is for.
      :type request: int
      :param exc: The exception.
      :type exc: Instance of :class:`Exception` or subclass thereof.
      """
      if isinstance(exc, exception.ApplicationError):
         msg = message.Error(request, exc.args[0], args = exc.args[1:], kwargs = exc.kwargs)
      else:
         if self._ecls_to_uri_pat.has_key(exc.__class__):
            error = self._ecls_to_uri_pat[exc.__class__][0]._uri
         else:
            error = "wamp.error.runtime_error"

         if hasattr(exc, 'args'):
            if hasattr(exc, 'kwargs'):
               msg = message.Error(request, error, args = exc.args, kwargs = exc.kwargs)
            else:
               msg = message.Error(request, error, args = exc.args)
         else:
            msg = message.Error(request, error)

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
class WampSession(WampBaseSession):

   def __init__(self):
      WampBaseSession.__init__(self)
      self._transport = None

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


   def onOpen(self, transport):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessageTransportHandler.onOpen`
      """
      self._transport = transport

      self._my_session_id = util.id()
      self._peer_session_id = None

      msg = message.Hello(self._my_session_id, [role.RoleBrokerFeatures()])
      self._transport.send(msg)


   def onMessage(self, msg):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessageTransportHandler.onMessage`
      """
      print "XXX", msg
      if self._peer_session_id is None:
         ## the first message MUST be HELLO
         if isinstance(msg, message.Hello):
            self._peer_session_id = msg.session
            self.onSessionOpen(self._my_session_id, self._peer_session_id)
         else:
            raise ProtocolError("Received {} message, and session is not yet established".format(message.__class__))
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
            self._transport.close()

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
               d = self._call_reqs.pop(msg.request)
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

            if msg.registration in self._registrations:
               endpoint = self._registrations[msg.registration]
               try:
                  if msg.kwargs:
                     if msg.args:
                        res = endpoint(*msg.args, **msg.kwargs)
                     else:
                        res = endpoint(**msg.kwargs)
                  else:
                     if msg.args:
                        res = endpoint(*msg.args)
                     else:
                        res = endpoint()
                  reply = message.Yield(msg.request, args = [res])
               except Exception as e:
                  reply = self._message_from_exception(msg.request, e)
               finally:
                  self._transport.send(reply)
            else:
               raise ProtocolError("INVOCATION received for non-registered registration ID {}".format(msg.registration))

         elif isinstance(msg, message.Registered):

            if msg.request in self._register_reqs:
               d, endpoint = self._register_reqs.pop(msg.request)
               self._registrations[msg.registration] = endpoint
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

            d = None

            if msg.request in self._publish_reqs:
               d = self._publish_reqs.pop(msg.request)

            elif msg.request in self._subscribe_reqs:
               d, _ = self._subscribe_reqs.pop(msg.request)

            elif msg.request in self._unsubscribe_reqs:
               d = self._unsubscribe_reqs.pop(msg.request)

            if d:
               d.errback(self._exception_from_message(msg))
            else:
               raise ProtocolError("ERROR received for non-pending request ID {}".format(msg.request))

         else:
            ## signal that we did not process the message
            return False

         ## signal that we have processed the message
         return True



   def onClose(self):
      """
      Implements :func:`autobahn.wamp.interfaces.IMessageTransportHandler.onClose`
      """
      self._transport = None


   def closeSession(self, reason = None, message = None):
      """
      Implements :func:`autobahn.wamp.interfaces.ISession.closeSession`
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

      d = Deferred()
      self._call_reqs[request] = d

      if 'options' in kwargs and isinstance(kwargs['options'], wamp.options.Call):
         opts = kwargs.pop('options')
         msg = message.Call(request, procedure, args = args, kwargs = kwargs, **opts.__dict__)
      else:
         msg = message.Call(request, procedure, args = args, kwargs = kwargs)

      self._transport.send(msg)
      return d


   def register(self, endpoint, procedure = None, options = None):
      """
      Implements :func:`autobahn.wamp.interfaces.ICallee.register`
      """
      assert(callable(endpoint))
      assert(type(procedure) in (str, unicode))
      assert(options is None or isinstance(options, wamp.options.Register))

      if not self._transport:
         raise exception.TransportLost()

      request = util.id()

      d = Deferred()
      self._register_reqs[request] = (d, endpoint)

      if options is not None:
         msg = message.Register(request, procedure, **options.__dict__)
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
