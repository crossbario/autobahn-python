###############################################################################
##
##  Copyright 2011,2012 Tavendo GmbH
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

import json
import random
import inspect, types
import traceback

import hashlib, hmac, binascii

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import Deferred, maybeDeferred

import autobahn

from websocket import WebSocketProtocol, HttpException
from websocket import WebSocketClientProtocol, WebSocketClientFactory
from websocket import WebSocketServerFactory, WebSocketServerProtocol

from httpstatus import HTTP_STATUS_CODE_BAD_REQUEST
from prefixmap import PrefixMap
from util import utcstr, utcnow, parseutc, newid


def exportRpc(arg = None):
   """
   Decorator for RPC'ed callables.
   """
   ## decorator without argument
   if type(arg) is types.FunctionType:
      arg._autobahn_rpc_id = arg.__name__
      return arg
   ## decorator with argument
   else:
      def inner(f):
         f._autobahn_rpc_id = arg
         return f
      return inner

def exportSub(arg, prefixMatch = False):
   """
   Decorator for subscription handlers.
   """
   def inner(f):
      f._autobahn_sub_id = arg
      f._autobahn_sub_prefix_match = prefixMatch
      return f
   return inner

def exportPub(arg, prefixMatch = False):
   """
   Decorator for publication handlers.
   """
   def inner(f):
      f._autobahn_pub_id = arg
      f._autobahn_pub_prefix_match = prefixMatch
      return f
   return inner


class WampProtocol:
   """
   WAMP protocol base class. Mixin for WampServerProtocol and WampClientProtocol.
   """

   URI_WAMP_BASE = "http://api.wamp.ws/"
   """
   WAMP base URI for WAMP predefined things.
   """

   URI_WAMP_ERROR = URI_WAMP_BASE + "error#"
   """
   Prefix for WAMP errors.
   """

   URI_WAMP_PROCEDURE = URI_WAMP_BASE + "procedure#"
   """
   Prefix for WAMP predefined RPC endpoints.
   """

   URI_WAMP_TOPIC = URI_WAMP_BASE + "topic#"
   """
   Prefix for WAMP predefined PubSub topics.
   """

   URI_WAMP_ERROR_GENERIC = URI_WAMP_ERROR + "generic"
   """
   WAMP error URI for generic errors.
   """

   DESC_WAMP_ERROR_GENERIC = "generic error"
   """
   Description for WAMP generic errors.
   """

   URI_WAMP_ERROR_INTERNAL = URI_WAMP_ERROR + "internal"
   """
   WAMP error URI for internal errors.
   """

   DESC_WAMP_ERROR_INTERNAL = "internal error"
   """
   Description for WAMP internal errors."
   """

   WAMP_PROTOCOL_VERSION         = 1
   """
   WAMP version this server speaks. Versions are numbered consecutively
   (integers, no gaps).
   """

   MESSAGE_TYPEID_WELCOME        = 0
   """
   Server-to-client welcome message containing session ID.
   """

   MESSAGE_TYPEID_PREFIX         = 1
   """
   Client-to-server message establishing a URI prefix to be used in CURIEs.
   """

   MESSAGE_TYPEID_CALL           = 2
   """
   Client-to-server message initiating an RPC.
   """

   MESSAGE_TYPEID_CALL_RESULT    = 3
   """
   Server-to-client message returning the result of a successful RPC.
   """

   MESSAGE_TYPEID_CALL_ERROR     = 4
   """
   Server-to-client message returning the error of a failed RPC.
   """

   MESSAGE_TYPEID_SUBSCRIBE      = 5
   """
   Client-to-server message subscribing to a topic.
   """

   MESSAGE_TYPEID_UNSUBSCRIBE    = 6
   """
   Client-to-server message unsubscribing from a topic.
   """

   MESSAGE_TYPEID_PUBLISH        = 7
   """
   Client-to-server message publishing an event to a topic.
   """

   MESSAGE_TYPEID_EVENT          = 8
   """
   Server-to-client message providing the event of a (subscribed) topic.
   """


   def connectionMade(self):
      self.debugWamp = self.factory.debugWamp
      self.debugApp = self.factory.debugApp
      self.prefixes = PrefixMap()


   def connectionLost(self, reason):
      pass


   def _protocolError(self, reason):
      if self.debugWamp:
         log.msg("Closing Wamp session on protocol violation : %s" % reason)

      ## FIXME: subprotocols are probably not supposed to close with CLOSE_STATUS_CODE_PROTOCOL_ERROR
      ##
      self.protocolViolation("Wamp RPC/PubSub protocol violation ('%s')" % reason)


   def shrink(self, uri, passthrough = False):
      """
      Shrink given URI to CURIE according to current prefix mapping.
      If no appropriate prefix mapping is available, return original URI.

      :param uri: URI to shrink.
      :type uri: str

      :returns str -- CURIE or original URI.
      """
      return self.prefixes.shrink(uri)


   def resolve(self, curieOrUri, passthrough = False):
      """
      Resolve given CURIE/URI according to current prefix mapping or return
      None if cannot be resolved.

      :param curieOrUri: CURIE or URI.
      :type curieOrUri: str

      :returns: str -- Full URI for CURIE or None.
      """
      return self.prefixes.resolve(curieOrUri)


   def resolveOrPass(self, curieOrUri):
      """
      Resolve given CURIE/URI according to current prefix mapping or return
      string verbatim if cannot be resolved.

      :param curieOrUri: CURIE or URI.
      :type curieOrUri: str

      :returns: str -- Full URI for CURIE or original string.
      """
      return self.prefixes.resolveOrPass(curieOrUri)



class WampFactory:
   """
   WAMP factory base class. Mixin for WampServerFactory and WampClientFactory.
   """

   pass



class WampServerProtocol(WebSocketServerProtocol, WampProtocol):
   """
   Server factory for Wamp RPC/PubSub.
   """

   SUBSCRIBE = 1
   PUBLISH = 2

   def onSessionOpen(self):
      """
      Callback fired when WAMP session was fully established.
      """
      pass


   def onOpen(self):
      """
      Default implementation for WAMP connection opened sends
      Welcome message containing session ID.
      """
      self.session_id = newid()
      msg = [WampProtocol.MESSAGE_TYPEID_WELCOME,
             self.session_id,
             WampProtocol.WAMP_PROTOCOL_VERSION,
             "Autobahn/%s" % autobahn.version]
      o = json.dumps(msg)
      self.sendMessage(o)
      self.factory._addSession(self, self.session_id)
      self.onSessionOpen()


   def onConnect(self, connectionRequest):
      """
      Default implementation for WAMP connection acceptance:
      check if client announced WAMP subprotocol, and only accept connection
      if client did so.
      """
      for p in connectionRequest.protocols:
         if p in self.factory.protocols:
            return p
      raise HttpException(HTTP_STATUS_CODE_BAD_REQUEST[0], "this server only speaks WAMP")


   def connectionMade(self):
      WebSocketServerProtocol.connectionMade(self)
      WampProtocol.connectionMade(self)

      ## RPCs registered in this session (a URI map of (object, procedure)
      ## pairs for object methods or (None, procedure) for free standing procedures)
      self.procs = {}

      ## Publication handlers registered in this session (a URI map of (object, pubHandler) pairs
      ## pairs for object methods (handlers) or (None, None) for topic without handler)
      self.pubHandlers = {}

      ## Subscription handlers registered in this session (a URI map of (object, subHandler) pairs
      ## pairs for object methods (handlers) or (None, None) for topic without handler)
      self.subHandlers = {}


   def connectionLost(self, reason):
      self.factory._unsubscribeClient(self)
      self.factory._removeSession(self)

      WampProtocol.connectionLost(self, reason)
      WebSocketServerProtocol.connectionLost(self, reason)


   def sendMessage(self, payload):
      if self.debugWamp:
         log.msg("TX WAMP: %s" % str(payload))
      WebSocketServerProtocol.sendMessage(self, payload)


   def _getPubHandler(self, topicUri):
      ## Longest matching prefix based resolution of (full) topic URI to
      ## publication handler.
      ## Returns a 5-tuple (consumedUriPart, unconsumedUriPart, handlerObj, handlerProc, prefixMatch)
      ##
      for i in xrange(len(topicUri), -1, -1):
         tt = topicUri[:i]
         if self.pubHandlers.has_key(tt):
            h = self.pubHandlers[tt]
            return (tt, topicUri[i:], h[0], h[1], h[2])
      return None


   def _getSubHandler(self, topicUri):
      ## Longest matching prefix based resolution of (full) topic URI to
      ## subscription handler.
      ## Returns a 5-tuple (consumedUriPart, unconsumedUriPart, handlerObj, handlerProc, prefixMatch)
      ##
      for i in xrange(len(topicUri), -1, -1):
         tt = topicUri[:i]
         if self.subHandlers.has_key(tt):
            h = self.subHandlers[tt]
            return (tt, topicUri[i:], h[0], h[1], h[2])
      return None


   def registerForPubSub(self, topicUri, prefixMatch = False, pubsub = PUBLISH | SUBSCRIBE):
      """
      Register a topic URI as publish/subscribe channel in this session.

      :param topicUri: Topic URI to be established as publish/subscribe channel.
      :type topicUri: str
      :param prefixMatch: Allow to match this topic URI by prefix.
      :type prefixMatch: bool
      :param pubsub: Allow publication and/or subscription.
      :type pubsub: WampServerProtocol.PUB, WampServerProtocol.SUB, WampServerProtocol.PUB | WampServerProtocol.SUB
      """
      if pubsub & WampServerProtocol.PUBLISH:
         self.pubHandlers[topicUri] = (None, None, prefixMatch)
         if self.debugWamp:
            log.msg("registered topic %s for publication (match by prefix = %s)" % (topicUri, prefixMatch))
      if pubsub & WampServerProtocol.SUBSCRIBE:
         self.subHandlers[topicUri] = (None, None, prefixMatch)
         if self.debugWamp:
            log.msg("registered topic %s for subscription (match by prefix = %s)" % (topicUri, prefixMatch))


   def registerHandlerForPubSub(self, obj, baseUri = ""):
      """
      Register a handler object for PubSub. A handler object has methods
      which are decorated using @exportPub and @exportSub.

      :param obj: The object to be registered (in this WebSockets session) for PubSub.
      :type obj: Object with methods decorated using @exportPub and @exportSub.
      :param baseUri: Optional base URI which is prepended to topic names for export.
      :type baseUri: String.
      """
      for k in inspect.getmembers(obj.__class__, inspect.ismethod):
         if k[1].__dict__.has_key("_autobahn_pub_id"):
            uri = baseUri + k[1].__dict__["_autobahn_pub_id"]
            prefixMatch = k[1].__dict__["_autobahn_pub_prefix_match"]
            proc = k[1]
            self.registerHandlerForPub(uri, obj, proc, prefixMatch)
         elif k[1].__dict__.has_key("_autobahn_sub_id"):
            uri = baseUri + k[1].__dict__["_autobahn_sub_id"]
            prefixMatch = k[1].__dict__["_autobahn_sub_prefix_match"]
            proc = k[1]
            self.registerHandlerForSub(uri, obj, proc, prefixMatch)


   def registerHandlerForSub(self, uri, obj, proc, prefixMatch = False):
      """
      Register a method of an object as subscription handler.

      :param uri: Topic URI to register subscription handler for.
      :type uri: str
      :param obj: The object on which to register a method as subscription handler.
      :type obj: object
      :param proc: Unbound object method to register as subscription handler.
      :type proc: unbound method
      :param prefixMatch: Allow to match this topic URI by prefix.
      :type prefixMatch: bool
      """
      self.subHandlers[uri] = (obj, proc, prefixMatch)
      if not self.pubHandlers.has_key(uri):
         self.pubHandlers[uri] = (None, None, False)
      if self.debugWamp:
         log.msg("registered subscription handler for topic %s" % uri)


   def registerHandlerForPub(self, uri, obj, proc, prefixMatch = False):
      """
      Register a method of an object as publication handler.

      :param uri: Topic URI to register publication handler for.
      :type uri: str
      :param obj: The object on which to register a method as publication handler.
      :type obj: object
      :param proc: Unbound object method to register as publication handler.
      :type proc: unbound method
      :param prefixMatch: Allow to match this topic URI by prefix.
      :type prefixMatch: bool
      """
      self.pubHandlers[uri] = (obj, proc, prefixMatch)
      if not self.subHandlers.has_key(uri):
         self.subHandlers[uri] = (None, None, False)
      if self.debugWamp:
         log.msg("registered publication handler for topic %s" % uri)


   def registerForRpc(self, obj, baseUri = "", methods = None):
      """
      Register an service object for RPC. A service object has methods
      which are decorated using @exportRpc.

      :param obj: The object to be registered (in this WebSockets session) for RPC.
      :type obj: Object with methods decorated using @exportRpc.
      :param baseUri: Optional base URI which is prepended to method names for export.
      :type baseUri: String.
      :param methods: If not None, a list of unbound class methods corresponding to obj
                     which should be registered. This can be used to register only a subset
                     of the methods decorated with @exportRpc.
      :type methods: List of unbound class methods.
      """
      for k in inspect.getmembers(obj.__class__, inspect.ismethod):
         if k[1].__dict__.has_key("_autobahn_rpc_id"):
            if methods is None or k[1] in methods:
               uri = baseUri + k[1].__dict__["_autobahn_rpc_id"]
               proc = k[1]
               self.registerMethodForRpc(uri, obj, proc)


   def registerMethodForRpc(self, uri, obj, proc):
      """
      Register a method of an object for RPC.

      :param uri: URI to register RPC method under.
      :type uri: str
      :param obj: The object on which to register a method for RPC.
      :type obj: object
      :param proc: Unbound object method to register RPC for.
      :type proc: unbound method
      """
      self.procs[uri] = (obj, proc, False)
      if self.debugWamp:
         log.msg("registered remote method on %s" % uri)


   def registerProcedureForRpc(self, uri, proc):
      """
      Register a (free standing) function/procedure for RPC.

      :param uri: URI to register RPC function/procedure under.
      :type uri: str
      :param proc: Free-standing function/procedure.
      :type proc: callable
      """
      self.procs[uri] = (None, proc, False)
      if self.debugWamp:
         log.msg("registered remote procedure on %s" % uri)


   def registerHandlerMethodForRpc(self, uri, obj, handler, extra = None):
      """
      Register a handler on an object for RPC.

      :param uri: URI to register RPC method under.
      :type uri: str
      :param obj: The object on which to register the RPC handler
      :type obj: object
      :param proc: Unbound object method to register RPC for.
      :type proc: unbound method
      :param extra: Optional extra data that will be given to the handler at call time.
      :type extra: object
      """
      self.procs[uri] = (obj, handler, True, extra)
      if self.debugWamp:
         log.msg("registered remote handler method on %s" % uri)


   def registerHandlerProcedureForRpc(self, uri, handler, extra = None):
      """
      Register a (free standing) handler for RPC.

      :param uri: URI to register RPC handler under.
      :type uri: str
      :param proc: Free-standing handler
      :type proc: callable
      :param extra: Optional extra data that will be given to the handler at call time.
      :type extra: object
      """
      self.procs[uri] = (None, handler, True, extra)
      if self.debugWamp:
         log.msg("registered remote handler procedure on %s" % uri)


   def dispatch(self, topicUri, event, exclude = [], eligible = None):
      """
      Dispatch an event for a topic to all clients subscribed to
      and authorized for that topic.

      Optionally, exclude list of clients and/or only consider clients
      from explicit eligibles. In other words, the event is delivered
      to the set

         (subscribers - excluded) & eligible

      :param topicUri: URI of topic to publish event to.
      :type topicUri: str
      :param event: Event to dispatch.
      :type event: obj
      :param exclude: Optional list of clients (WampServerProtocol instances) to exclude.
      :type exclude: list of obj
      :param eligible: Optional list of clients (WampServerProtocol instances) eligible at all (or None for all).
      :type eligible: list of obj
      """
      self.factory.dispatch(topicUri, event, exclude, eligible)


   def _callProcedure(self, callid, uri, args = None):
      """
      INTERNAL METHOD! Actually performs the call of a procedure invoked via RPC.
      """

      uri, args = self.onBeforeCall(callid, uri, args, self.procs.has_key(uri))

      if self.procs.has_key(uri):
         m = self.procs[uri]
         if not m[2]:
            ## RPC method/procedure
            ##
            if args:
               ## method/function called with args
               cargs = tuple(args)
               if m[0]:
                  ## call object method
                  return m[1](m[0], *cargs)
               else:
                  ## call free-standing function/procedure
                  return m[1](*cargs)
            else:
               ## method/function called without args
               if m[0]:
                  ## call object method
                  return m[1](m[0])
               else:
                  ## call free-standing function/procedure
                  return m[1]()
         else:
            ## RPC handler
            ##
            if m[0]:
               ## call RPC handler on object
               return m[1](m[0], uri, args, m[3])
            else:
               ## call free-standing RPC handler
               return m[1](uri, args, m[3])
      else:
         raise Exception("no procedure %s" % uri)


   def onBeforeCall(self, callid, uri, args, isRegistered):
      """
      Callback fired before executing incoming RPC. This can be used for
      logging, statistics tracking or redirecting RPCs or argument mangling i.e.

      The default implementation just returns the incoming URI/args.

      :param uri: RPC endpoint URI (fully-qualified).
      :type uri: str
      :param args: RPC arguments array.
      :type args: list
      :param isRegistered: True, iff RPC endpoint URI is registered in this session.
      :type isRegistered: bool
      :returns pair -- Must return URI/Args pair.
      """
      return uri, args


   def onAfterCallSuccess(self, result, callid):
      """
      Callback fired after executing incoming RPC with success.

      The default implementation will just return `result` to the client.

      :param result: Result returned for executing the incoming RPC.
      :type result: Anything returned by the user code for the endpoint.
      :param callid: WAMP call ID for incoming RPC.
      :type callid: str
      :returns obj -- Result send back to client.
      """
      return result


   def onAfterCallError(self, error, callid):
      """
      Callback fired after executing incoming RPC with failure.

      The default implementation will just return `error` to the client.

      :param error: Error that occurred during incomnig RPC call execution.
      :type error: Instance of twisted.python.failure.Failure
      :param callid: WAMP call ID for incoming RPC.
      :type callid: str
      :returns twisted.python.failure.Failure -- Error send back to client.
      """
      return error


   def _sendCallResult(self, result, callid):
      """
      INTERNAL METHOD! Marshal and send a RPC success result.
      """
      msg = [WampProtocol.MESSAGE_TYPEID_CALL_RESULT, callid, result]
      try:
         rmsg = json.dumps(msg)
      except:
         raise Exception("call result not JSON serializable")
      else:
         self.sendMessage(rmsg)


   def _sendCallError(self, error, callid):
      """
      INTERNAL METHOD! Marshal and send a RPC error result.
      """
      try:

         eargs = error.value.args
         leargs = len(eargs)
         traceb = error.getTraceback()

         if leargs == 0:
            erroruri = WampProtocol.URI_WAMP_ERROR_GENERIC
            errordesc = WampProtocol.DESC_WAMP_ERROR_GENERIC
            errordetails = None

         elif leargs == 1:
            if type(eargs[0]) not in [str, unicode]:
               raise Exception("invalid type %s for errorDesc" % type(eargs[0]))
            erroruri = WampProtocol.URI_WAMP_ERROR_GENERIC
            errordesc = eargs[0]
            errordetails = None

         elif leargs in [2, 3]:
            if type(eargs[0]) not in [str, unicode]:
               raise Exception("invalid type %s for errorUri" % type(eargs[0]))
            erroruri = eargs[0]
            if type(eargs[1]) not in [str, unicode]:
               raise Exception("invalid type %s for errorDesc" % type(eargs[1]))
            errordesc = eargs[1]
            if leargs > 2:
               errordetails = eargs[2] # this must be JSON serializable .. if not, we get exception later in sendMessage
            else:
               errordetails = None

         else:
            raise Exception("invalid args length %d for exception" % leargs)

         if errordetails is not None:
            msg = [WampProtocol.MESSAGE_TYPEID_CALL_ERROR, callid, self.prefixes.shrink(erroruri), errordesc, errordetails]
         else:
            msg = [WampProtocol.MESSAGE_TYPEID_CALL_ERROR, callid, self.prefixes.shrink(erroruri), errordesc]

         try:
            rmsg = json.dumps(msg)
         except Exception, e:
            raise Exception("invalid object for errorDetails - not JSON serializable (%s)" % str(e))

         if self.debugApp:
            log.msg("application error")
            log.msg(traceb)
            log.msg(msg)

      except Exception, e:

         if self.debugWamp:
            log.err(str(e))
            log.err(error.getTraceback())

         msg = [WampProtocol.MESSAGE_TYPEID_CALL_ERROR, callid, self.prefixes.shrink(WampProtocol.URI_WAMP_ERROR_INTERNAL), WampProtocol.DESC_WAMP_ERROR_INTERNAL]
         rmsg = json.dumps(msg)

      finally:

         self.sendMessage(rmsg)


   def onMessage(self, msg, binary):
      """
      INTERNAL METHOD! Handle WAMP messages received from WAMP client.
      """

      if self.debugWamp:
         log.msg("RX WAMP: %s" % str(msg))

      if not binary:
         try:
            obj = json.loads(msg)
            if type(obj) == list:

               ## Call Message
               ##
               if obj[0] == WampProtocol.MESSAGE_TYPEID_CALL:

                  ## incoming RPC parameters
                  callid = obj[1]
                  procuri = self.prefixes.resolveOrPass(obj[2])
                  args = obj[3:]

                  ## execute incoming RPC
                  d = maybeDeferred(self._callProcedure, callid, procuri, args)

                  ## wire up after call user callbacks
                  d.addCallback(self.onAfterCallSuccess, callid)
                  d.addErrback(self.onAfterCallError, callid)

                  ## wire up pack & send WAMP message
                  d.addCallback(self._sendCallResult, callid)
                  d.addErrback(self._sendCallError, callid)

               ## Subscribe Message
               ##
               elif obj[0] == WampProtocol.MESSAGE_TYPEID_SUBSCRIBE:
                  topicUri = self.prefixes.resolveOrPass(obj[1])
                  h = self._getSubHandler(topicUri)
                  if h:
                     ## either exact match or prefix match allowed
                     if h[1] == "" or h[4]:

                        ## direct topic
                        if h[2] is None and h[3] is None:
                           self.factory._subscribeClient(self, topicUri)

                        ## topic handled by subscription handler
                        else:
                           try:
                              ## handler is object method
                              if h[2]:
                                 a = h[3](h[2], str(h[0]), str(h[1]))

                              ## handler is free standing procedure
                              else:
                                 a = h[3](str(h[0]), str(h[1]))

                              ## only subscribe client if handler did return True
                              if a:
                                 self.factory._subscribeClient(self, topicUri)
                           except:
                              if self.debugWamp:
                                 log.msg("execption during topic subscription handler")
                     else:
                        if self.debugWamp:
                           log.msg("topic %s matches only by prefix and prefix match disallowed" % topicUri)
                  else:
                     if self.debugWamp:
                        log.msg("no topic / subscription handler registered for %s" % topicUri)

               ## Unsubscribe Message
               ##
               elif obj[0] == WampProtocol.MESSAGE_TYPEID_UNSUBSCRIBE:
                  topicUri = self.prefixes.resolveOrPass(obj[1])
                  self.factory._unsubscribeClient(self, topicUri)

               ## Publish Message
               ##
               elif obj[0] == WampProtocol.MESSAGE_TYPEID_PUBLISH:
                  topicUri = self.prefixes.resolveOrPass(obj[1])
                  h = self._getPubHandler(topicUri)
                  if h:
                     ## either exact match or prefix match allowed
                     if h[1] == "" or h[4]:

                        ## Event
                        ##
                        event = obj[2]

                        ## Exclude Sessions List
                        ##
                        exclude = [self] # exclude publisher by default
                        if len(obj) >= 4:
                           if type(obj[3]) == bool:
                              if not obj[3]:
                                 exclude = []
                           elif type(obj[3]) == list:
                              ## map session IDs to protos
                              exclude = self.factory.sessionIdsToProtos(obj[3])
                           else:
                              ## FIXME: invalid type
                              pass

                        ## Eligible Sessions List
                        ##
                        eligible = None # all sessions are eligible by default
                        if len(obj) >= 5:
                           if type(obj[4]) == list:
                              ## map session IDs to protos
                              eligible = self.factory.sessionIdsToProtos(obj[4])
                           else:
                              ## FIXME: invalid type
                              pass

                        ## direct topic
                        if h[2] is None and h[3] is None:
                           self.factory.dispatch(topicUri, event, exclude, eligible)

                        ## topic handled by publication handler
                        else:
                           try:
                              ## handler is object method
                              if h[2]:
                                 e = h[3](h[2], str(h[0]), str(h[1]), event)

                              ## handler is free standing procedure
                              else:
                                 e = h[3](str(h[0]), str(h[1]), event)

                              ## only dispatch event if handler did return event
                              if e:
                                 self.factory.dispatch(topicUri, e, exclude, eligible)
                           except:
                              if self.debugWamp:
                                 log.msg("execption during topic publication handler")
                     else:
                        if self.debugWamp:
                           log.msg("topic %s matches only by prefix and prefix match disallowed" % topicUri)
                  else:
                     if self.debugWamp:
                        log.msg("no topic / publication handler registered for %s" % topicUri)

               ## Define prefix to be used in CURIEs
               ##
               elif obj[0] == WampProtocol.MESSAGE_TYPEID_PREFIX:
                  prefix = obj[1]
                  uri = obj[2]
                  self.prefixes.set(prefix, uri)

               else:
                  log.msg("unknown message type")
            else:
               log.msg("msg not a list")
         except Exception, e:
            traceback.print_exc()
      else:
         log.msg("binary message")



class WampServerFactory(WebSocketServerFactory, WampFactory):
   """
   Server factory for Wamp RPC/PubSub.
   """

   protocol = WampServerProtocol
   """
   Twisted protocol used by default for WAMP servers.
   """

   def __init__(self, url, debug = False, debugCodePaths = False, debugWamp = False, debugApp = False):
      WebSocketServerFactory.__init__(self, url, protocols = ["wamp"], debug = debug, debugCodePaths = debugCodePaths)
      self.debugWamp = debugWamp
      self.debugApp = debugApp


   def onClientSubscribed(self, proto, topicUri):
      """
      Callback fired when peer was (successfully) subscribed on some topic.

      :param proto: Peer protocol instance subscribed.
      :type proto: Instance of WampServerProtocol.
      :param topicUri: Fully qualified, resolved URI of topic subscribed.
      :type topicUri: str
      """
      pass


   def _subscribeClient(self, proto, topicUri):
      """
      INTERNAL METHOD! Called from proto to subscribe client for topic.
      """
      if not self.subscriptions.has_key(topicUri):
         self.subscriptions[topicUri] = set()
         if self.debugWamp:
            log.msg("subscriptions map created for topic %s" % topicUri)
      if not proto in self.subscriptions[topicUri]:
         self.subscriptions[topicUri].add(proto)
         if self.debugWamp:
            log.msg("subscribed peer %s on topic %s" % (proto.peerstr, topicUri))
         self.onClientSubscribed(proto, topicUri)
      else:
         if self.debugWamp:
            log.msg("peer %s already subscribed on topic %s" % (proto.peerstr, topicUri))


   def onClientUnsubscribed(self, proto, topicUri):
      """
      Callback fired when peer was (successfully) unsubscribed from some topic.

      :param proto: Peer protocol instance unsubscribed.
      :type proto: Instance of WampServerProtocol.
      :param topicUri: Fully qualified, resolved URI of topic unsubscribed.
      :type topicUri: str
      """
      pass


   def _unsubscribeClient(self, proto, topicUri = None):
      """
      INTERNAL METHOD! Called from proto to unsubscribe client from topic.
      """
      if topicUri:
         if self.subscriptions.has_key(topicUri) and proto in self.subscriptions[topicUri]:
            self.subscriptions[topicUri].discard(proto)
            if self.debugWamp:
               log.msg("unsubscribed peer %s from topic %s" % (proto.peerstr, topicUri))
            if len(self.subscriptions[topicUri]) == 0:
               del self.subscriptions[topicUri]
               if self.debugWamp:
                  log.msg("topic %s removed from subscriptions map - no one subscribed anymore" % topicUri)
            self.onClientUnsubscribed(proto, topicUri)
         else:
            if self.debugWamp:
               log.msg("peer %s not subscribed on topic %s" % (proto.peerstr, topicUri))
      else:
         for topicUri, subscribers in self.subscriptions.items():
            if proto in subscribers:
               subscribers.discard(proto)
               if self.debugWamp:
                  log.msg("unsubscribed peer %s from topic %s" % (proto.peerstr, topicUri))
               if len(subscribers) == 0:
                  del self.subscriptions[topicUri]
                  if self.debugWamp:
                     log.msg("topic %s removed from subscriptions map - no one subscribed anymore" % topicUri)
               self.onClientUnsubscribed(proto, topicUri)
         if self.debugWamp:
            log.msg("unsubscribed peer %s from all topics" % (proto.peerstr))


   def dispatch(self, topicUri, event, exclude = [], eligible = None):
      """
      Dispatch an event to all peers subscribed to the event topic.

      :param topicUri: Topic to publish event to.
      :type topicUri: str
      :param event: Event to publish (must be JSON serializable).
      :type event: obj
      :param exclude: List of WampServerProtocol instances to exclude from receivers.
      :type exclude: List of obj
      :param eligible: List of WampServerProtocol instances eligible as receivers (or None for all).
      :type eligible: List of obj

      :returns twisted.internet.defer.Deferred -- Will be fired when event was
      dispatched to all subscribers. The return value provided to the deferred
      is a pair (delivered, requested), where delivered = number of actual
      receivers, and requested = number of (subscribers - excluded) & eligible.
      """
      if self.debugWamp:
         log.msg("publish event %s for topicUri %s" % (str(event), topicUri))

      d = Deferred()

      if self.subscriptions.has_key(topicUri) and len(self.subscriptions[topicUri]) > 0:

         ## FIXME: this might break ordering of event delivery from a
         ## receiver perspective. We might need to have send queues
         ## per receiver OR do recvs = deque(sorted(..))

         ## However, see http://twistedmatrix.com/trac/ticket/1396

         if eligible is not None:
            subscrbs = set(eligible) & self.subscriptions[topicUri]
         else:
            subscrbs = self.subscriptions[topicUri]

         if len(exclude) > 0:
            recvs = subscrbs - set(exclude)
         else:
            recvs = subscrbs

         l = len(recvs)
         if l > 0:

            ## ok, at least 1 subscriber not excluded and eligible
            ## => prepare message for mass sending
            ##
            o = [WampProtocol.MESSAGE_TYPEID_EVENT, topicUri, event]
            try:
               msg = json.dumps(o)
               if self.debugWamp:
                  log.msg("serialized event msg: " + str(msg))
            except:
               raise Exception("invalid type for event (not JSON serializable)")

            preparedMsg = self.prepareMessage(msg)

            ## chunked sending of prepared message
            ##
            self._sendEvents(preparedMsg, recvs.copy(), 0, l, d)

         else:
            ## receivers list empty after considering exlude and eligible sessions
            ##
            d.callback((0, 0))
      else:
         ## no one subscribed on topic
         ##
         d.callback((0, 0))

      return d


   def _sendEvents(self, preparedMsg, recvs, delivered, requested, d):
      """
      INTERNAL METHOD! Delivers events to receivers in chunks and
      reenters the reactor in-between, so that other stuff can run.
      """
      ## deliver a batch of events
      done = False
      for i in xrange(0, 256):
         try:
            proto = recvs.pop()
            if proto.state == WebSocketProtocol.STATE_OPEN:
               try:
                  proto.sendPreparedMessage(preparedMsg)
               except:
                  pass
               else:
                  if self.debugWamp:
                     log.msg("delivered event to peer %s" % proto.peerstr)
                  delivered += 1
         except KeyError:
            # all receivers done
            done = True
            break

      if not done:
         ## if there are receivers left, redo
         reactor.callLater(0, self._sendEvents, preparedMsg, recvs, delivered, requested, d)
      else:
         ## else fire final result
         d.callback((delivered, requested))


   def _addSession(self, proto, session_id):
      """
      INTERNAL METHOD! Add proto for session ID.
      """
      if not self.protoToSessions.has_key(proto):
         self.protoToSessions[proto] = session_id
      else:
         raise Exception("logic error - dublicate _addSession for protoToSessions")
      if not self.sessionsToProto.has_key(session_id):
         self.sessionsToProto[session_id] = proto
      else:
         raise Exception("logic error - dublicate _addSession for sessionsToProto")


   def _removeSession(self, proto):
      """
      INTERNAL METHOD! Remove session by proto.
      """
      if self.protoToSessions.has_key(proto):
         session_id = self.protoToSessions[proto]
         del self.protoToSessions[proto]
         if self.sessionsToProto.has_key(session_id):
            del self.sessionsToProto[session_id]


   def sessionIdsToProtos(self, sessionIds):
      """
      Map session IDs to connected client protocol instances.

      :param sessionIds: List of session IDs to be mapped.
      :type sessionIds: list of str

      :returns list of WampServerProtocol instances -- List of protocol instances corresponding to the session IDs.
      """
      protos = []
      for s in sessionIds:
         if self.sessionsToProto.has_key(s):
            protos.append(self.sessionsToProto[s])
      return protos


   def protosToSessionIds(self, protos):
      """
      Map connected client protocol instances to session IDs.

      :param protos: List of instances of WampServerProtocol to be mapped.
      :type protos: list of WampServerProtocol

      :returns list of str -- List of session IDs corresponding to the protos.
      """
      sessionIds = []
      for p in protos:
         if self.protoToSessions.has_key(p):
            sessionIds.append(self.protoToSessions[p])
      return sessionIds


   def startFactory(self):
      """
      Called by Twisted when the factory starts up. When overriding, make
      sure to call the base method.
      """
      if self.debugWamp:
         log.msg("WampServerFactory starting")
      self.subscriptions = {}
      self.protoToSessions = {}
      self.sessionsToProto = {}


   def stopFactory(self):
      """
      Called by Twisted when the factory shuts down. When overriding, make
      sure to call the base method.
      """
      if self.debugWamp:
         log.msg("WampServerFactory stopped")



class WampClientProtocol(WebSocketClientProtocol, WampProtocol):
   """
   Twisted client protocol for WAMP.
   """

   def onSessionOpen(self):
      """
      Callback fired when WAMP session was fully established. Override
      in derived class.
      """
      pass


   def onOpen(self):
      ## do nothing here .. onSessionOpen is only fired when welcome
      ## message was received (and thus session ID set)
      pass


   def onConnect(self, connectionResponse):
      if connectionResponse.protocol not in self.factory.protocols:
         raise Exception("server does not speak WAMP")


   def connectionMade(self):
      WebSocketClientProtocol.connectionMade(self)
      WampProtocol.connectionMade(self)

      self.calls = {}
      self.subscriptions = {}


   def connectionLost(self, reason):
      WampProtocol.connectionLost(self, reason)
      WebSocketClientProtocol.connectionLost(self, reason)


   def sendMessage(self, payload):
      if self.debugWamp:
         log.msg("TX WAMP: %s" % str(payload))
      WebSocketClientProtocol.sendMessage(self, payload)


   def onMessage(self, msg, binary):
      """Internal method to handle WAMP messages received from WAMP server."""

      ## WAMP is text message only
      ##
      if binary:
         self._protocolError("binary WebSocket message received")
         return

      if self.debugWamp:
         log.msg("RX WAMP: %s" % str(msg))

      ## WAMP is proper JSON payload
      ##
      try:
         obj = json.loads(msg)
      except:
         self._protocolError("WAMP message payload not valid JSON")
         return

      ## Every WAMP message is a list
      ##
      if type(obj) != list:
         self._protocolError("WAMP message payload not a list")
         return

      ## Every WAMP message starts with an integer for message type
      ##
      if len(obj) < 1:
         self._protocolError("WAMP message without message type")
         return
      if type(obj[0]) != int:
         self._protocolError("WAMP message type not an integer")
         return

      ## WAMP message type
      ##
      msgtype = obj[0]

      ## Valid WAMP message types received by WAMP clients
      ##
      if msgtype not in [WampProtocol.MESSAGE_TYPEID_WELCOME,
                         WampProtocol.MESSAGE_TYPEID_CALL_RESULT,
                         WampProtocol.MESSAGE_TYPEID_CALL_ERROR,
                         WampProtocol.MESSAGE_TYPEID_EVENT]:
         self._protocolError("invalid WAMP message type %d" % msgtype)
         return

      ## WAMP CALL_RESULT / CALL_ERROR
      ##
      if msgtype in [WampProtocol.MESSAGE_TYPEID_CALL_RESULT, WampProtocol.MESSAGE_TYPEID_CALL_ERROR]:

         ## Call ID
         ##
         if len(obj) < 2:
            self._protocolError("WAMP CALL_RESULT/CALL_ERROR message without <callid>")
            return
         if type(obj[1]) not in [unicode, str]:
            self._protocolError("WAMP CALL_RESULT/CALL_ERROR message with invalid type %s for <callid>" % type(obj[1]))
            return
         callid = str(obj[1])

         ## Pop and process Call Deferred
         ##
         d = self.calls.pop(callid, None)
         if d:
            ## WAMP CALL_RESULT
            ##
            if msgtype == WampProtocol.MESSAGE_TYPEID_CALL_RESULT:
               ## Call Result
               ##
               if len(obj) != 3:
                  self._protocolError("WAMP CALL_RESULT message with invalid length %d" % len(obj))
                  return
               result = obj[2]

               ## Fire Call Success Deferred
               ##
               d.callback(result)

            ## WAMP CALL_ERROR
            ##
            elif msgtype == WampProtocol.MESSAGE_TYPEID_CALL_ERROR:
               if len(obj) not in [4, 5]:
                  self._protocolError("call error message invalid length %d" % len(obj))
                  return

               ## Error URI
               ##
               if type(obj[2]) not in [unicode, str]:
                  self._protocolError("invalid type %s for errorUri in call error message" % str(type(obj[2])))
                  return
               erroruri = str(obj[2])

               ## Error Description
               ##
               if type(obj[3]) not in [unicode, str]:
                  self._protocolError("invalid type %s for errorDesc in call error message" % str(type(obj[3])))
                  return
               errordesc = str(obj[3])

               ## Error Details
               ##
               if len(obj) > 4:
                  errordetails = obj[4]
               else:
                  errordetails = None

               ## Fire Call Error Deferred
               ##
               e = Exception()
               e.args = (erroruri, errordesc, errordetails)
               d.errback(e)
            else:
               raise Exception("logic error")
         else:
            if self.debugWamp:
               log.msg("callid not found for received call result/error message")

      ## WAMP EVENT
      ##
      elif msgtype == WampProtocol.MESSAGE_TYPEID_EVENT:
         ## Topic
         ##
         if len(obj) != 3:
            self._protocolError("WAMP EVENT message invalid length %d" % len(obj))
            return
         if type(obj[1]) not in [unicode, str]:
            self._protocolError("invalid type for <topic> in WAMP EVENT message")
            return
         unresolvedTopicUri = str(obj[1])
         topicUri = self.prefixes.resolveOrPass(unresolvedTopicUri)

         ## Fire PubSub Handler
         ##
         if self.subscriptions.has_key(topicUri):
            event = obj[2]
            self.subscriptions[topicUri](topicUri, event)
         else:
            ## event received for non-subscribed topic (could be because we
            ## just unsubscribed, and server already sent out event for
            ## previous subscription)
            pass

      ## WAMP WELCOME
      ##
      elif msgtype == WampProtocol.MESSAGE_TYPEID_WELCOME:
         ## Session ID
         ##
         if len(obj) < 2:
            self._protocolError("WAMP WELCOME message invalid length %d" % len(obj))
            return
         if type(obj[1]) not in [unicode, str]:
            self._protocolError("invalid type for <sessionid> in WAMP WELCOME message")
            return
         self.session_id = str(obj[1])

         ## WAMP Protocol Version
         ##
         if len(obj) > 2:
            if type(obj[2]) not in [int]:
               self._protocolError("invalid type for <version> in WAMP WELCOME message")
               return
            else:
               self.session_protocol_version = obj[2]
         else:
            self.session_protocol_version = None

         ## Server Ident
         ##
         if len(obj) > 3:
            if type(obj[3]) not in [unicode, str]:
               self._protocolError("invalid type for <server> in WAMP WELCOME message")
               return
            else:
               self.session_server = obj[3]
         else:
            self.session_server = None

         self.onSessionOpen()

      else:
         raise Exception("logic error")


   def call(self, *args):
      """
      Perform a remote-procedure call (RPC). The first argument is the procedure
      URI (mandatory). Subsequent positional arguments can be provided (must be
      JSON serializable). The return value is a Twisted Deferred.
      """

      if len(args) < 1:
         raise Exception("missing procedure URI")

      if type(args[0]) not in [unicode, str]:
         raise Exception("invalid type for procedure URI")

      procuri = args[0]
      while True:
         callid = newid()
         if not self.calls.has_key(callid):
            break
      d = Deferred()
      self.calls[callid] = d
      msg = [WampProtocol.MESSAGE_TYPEID_CALL, callid, procuri]
      msg.extend(args[1:])

      try:
         o = json.dumps(msg)
      except:
         raise Exception("call argument(s) not JSON serializable")

      self.sendMessage(o)
      return d


   def prefix(self, prefix, uri):
      """
      Establishes a prefix to be used in CURIEs instead of URIs having that
      prefix for both client-to-server and server-to-client messages.

      :param prefix: Prefix to be used in CURIEs.
      :type prefix: str
      :param uri: URI that this prefix will resolve to.
      :type uri: str
      """

      if type(prefix) != str:
         raise Exception("invalid type for prefix")

      if type(uri) not in [unicode, str]:
         raise Exception("invalid type for URI")

      if self.prefixes.get(prefix):
         raise Exception("prefix already defined")

      self.prefixes.set(prefix, uri)

      msg = [WampProtocol.MESSAGE_TYPEID_PREFIX, prefix, uri]

      self.sendMessage(json.dumps(msg))


   def publish(self, topicUri, event, excludeMe = None, exclude = None, eligible = None):
      """
      Publish an event under a topic URI. The latter may be abbreviated using a
      CURIE which has been previously defined using prefix(). The event must
      be JSON serializable.

      :param topicUri: The topic URI or CURIE.
      :type topicUri: str
      :param event: Event to be published (must be JSON serializable) or None.
      :type event: value
      :param excludeMe: When True, don't deliver the published event to myself (when I'm subscribed).
      :type excludeMe: bool
      :param exclude: Optional list of session IDs to exclude from receivers.
      :type exclude: list of str
      :param eligible: Optional list of session IDs to that are eligible as receivers.
      :type eligible: list of str
      """

      if type(topicUri) not in [unicode, str]:
         raise Exception("invalid type for parameter 'topicUri' - must be string (was %s)" % type(topicUri))

      if excludeMe is not None:
         if type(excludeMe) != bool:
            raise Exception("invalid type for parameter 'excludeMe' - must be bool (was %s)" % type(excludeMe))

      if exclude is not None:
         if type(exclude) != list:
            raise Exception("invalid type for parameter 'exclude' - must be list (was %s)" % type(exclude))

      if eligible is not None:
         if type(eligible) != list:
            raise Exception("invalid type for parameter 'eligible' - must be list (was %s)" % type(eligible))

      if exclude is not None or eligible is not None:
         if exclude is None:
            if excludeMe is not None:
               if excludeMe:
                  exclude = [self.session_id]
               else:
                  exclude = []
            else:
               exclude = [self.session_id]
         if eligible is not None:
            msg = [WampProtocol.MESSAGE_TYPEID_PUBLISH, topicUri, event, exclude, eligible]
         else:
            msg = [WampProtocol.MESSAGE_TYPEID_PUBLISH, topicUri, event, exclude]
      else:
         if excludeMe:
            msg = [WampProtocol.MESSAGE_TYPEID_PUBLISH, topicUri, event]
         else:
            msg = [WampProtocol.MESSAGE_TYPEID_PUBLISH, topicUri, event, excludeMe]

      try:
         o = json.dumps(msg)
      except:
         raise Exception("invalid type for parameter 'event' - not JSON serializable")

      self.sendMessage(o)


   def subscribe(self, topicUri, handler):
      """
      Subscribe to topic. When already subscribed, will overwrite the handler.

      :param topicUri: URI or CURIE of topic to subscribe to.
      :type topicUri: str
      :param handler: Event handler to be invoked upon receiving events for topic.
      :type handler: Python callable, will be called as in <callable>(eventUri, event).
      """
      if type(topicUri) not in [unicode, str]:
         raise Exception("invalid type for parameter 'topicUri' - must be string (was %s)" % type(topicUri))

      if type(handler) not in [types.FunctionType, types.MethodType, types.BuiltinFunctionType, types.BuiltinMethodType]:
         raise Exception("invalid type for parameter 'handler' - must be a callable (was %s)" % type(handler))

      turi = self.prefixes.resolveOrPass(topicUri)
      if not self.subscriptions.has_key(turi):
         msg = [WampProtocol.MESSAGE_TYPEID_SUBSCRIBE, topicUri]
         o = json.dumps(msg)
         self.sendMessage(o)
      self.subscriptions[turi] = handler


   def unsubscribe(self, topicUri):
      """
      Unsubscribe from topic. Will do nothing when currently not subscribed to the topic.

      :param topicUri: URI or CURIE of topic to unsubscribe from.
      :type topicUri: str
      """
      if type(topicUri) not in [unicode, str]:
         raise Exception("invalid type for parameter 'topicUri' - must be string (was %s)" % type(topicUri))

      turi = self.prefixes.resolveOrPass(topicUri)
      if self.subscriptions.has_key(turi):
         msg = [WampProtocol.MESSAGE_TYPEID_UNSUBSCRIBE, topicUri]
         o = json.dumps(msg)
         self.sendMessage(o)
         del self.subscriptions[turi]



class WampClientFactory(WebSocketClientFactory, WampFactory):
   """
   Twisted client factory for WAMP.
   """

   protocol = WampClientProtocol

   def __init__(self, url, debug = False, debugCodePaths = False, debugWamp = False, debugApp = False):
      WebSocketClientFactory.__init__(self, url, protocols = ["wamp"], debug = debug, debugCodePaths = debugCodePaths)
      self.debugWamp = debugWamp
      self.debugApp = debugApp


   def startFactory(self):
      """
      Called by Twisted when the factory starts up. When overriding, make
      sure to call the base method.
      """
      if self.debugWamp:
         log.msg("WebSocketClientFactory starting")


   def stopFactory(self):
      """
      Called by Twisted when the factory shuts down. When overriding, make
      sure to call the base method.
      """
      if self.debugWamp:
         log.msg("WebSocketClientFactory stopped")



class WampCraProtocol(WampProtocol):
   """
   Base class for WAMP Challenge-Response Authentication protocols (client and server).

   WAMP-CRA is a cryptographically strong challenge response authentication
   protocol based on HMAC-SHA256.

   The protocol performs in-band authentication of WAMP clients to WAMP servers.

   WAMP-CRA does not introduce any new WAMP protocol level message types, but
   implements the authentication handshake via standard WAMP RPCs with well-known
   procedure URIs and signatures.
   """

   def authSignature(self, authChallenge, authSecret = None):
      """
      Compute the authentication signature from an authentication challenge and a secret.

      :param authChallenge: The authentication challenge.
      :type authChallenge: str
      :param authSecret: The authentication secret.
      :type authSecret: str

      :returns str -- The authentication signature.
      """
      if authSecret is None:
         authSecret = ""
      h = hmac.new(authSecret, authChallenge, hashlib.sha256)
      sig = binascii.b2a_base64(h.digest()).strip()
      return sig



class WampCraClientProtocol(WampClientProtocol, WampCraProtocol):
   """
   Simple, authenticated WAMP client protocol.

   The client can perform WAMP-Challenge-Response-Authentication ("WAMP-CRA") to authenticate
   itself to a WAMP server. The server needs to implement WAMP-CRA also of course.
   """

   def authenticate(self, authKey = None, authExtra = None, authSecret = None):
      """
      Authenticate the WAMP session to server.

      :param authKey: The key of the authentication credentials, something like a user or application name.
      :type authKey: str
      :param authExtra: Any extra authentication information.
      :type authExtra: dict
      :param authSecret: The secret of the authentication credentials, something like the user password or application secret key.
      :type authsecret: str

      :returns Deferred -- Deferred that fires upon authentication success (with permissions) or failure.
      """

      def _onAuthChallenge(challenge):
         if authKey is not None:
            sig = self.authSignature(challenge, authSecret)
         else:
            sig = None
         d = self.call(WampProtocol.URI_WAMP_PROCEDURE + "auth", sig)
         return d

      d = self.call(WampProtocol.URI_WAMP_PROCEDURE + "authreq", authKey, authExtra)
      d.addCallback(_onAuthChallenge)
      return d



class WampCraServerProtocol(WampServerProtocol, WampCraProtocol):
   """
   Simple, authenticating WAMP server protocol.

   The server lets clients perform WAMP-Challenge-Response-Authentication ("WAMP-CRA")
   to authenticate. The clients need to implement WAMP-CRA also of course.

   To implement an authenticating server, override:

      * getAuthSecret
      * getAuthPermissions
      * onAuthenticated

   in your class deriving from this class.
   """

   clientAuthTimeout = 0
   """
   Client authentication timeout in seconds or 0 for infinite. A client
   must perform authentication after the initial WebSocket handshake within
   this timeout or the connection is failed.
   """

   clientAuthAllowAnonymous = True
   """
   Allow anonymous client authentication. When this is set to True, a client
   may "authenticate" as anonymous.
   """


   def getAuthPermissions(self, authKey, authExtra):
      """
      Get the permissions the session is granted when the authentication succeeds
      for the given key / extra information.

      Override in derived class to implement your authentication.

      A permissions object is structured like this::

         {'permissions': {'rpc': [
                                    {'uri':  / RPC Endpoint URI - String /,
                                     'call': / Allow to call? - Boolean /}
                                 ],
                          'pubsub': [
                                       {'uri':    / PubSub Topic URI / URI prefix - String /,
                                        'prefix': / URI matched by prefix? - Boolean /,
                                        'pub':    / Allow to publish? - Boolean /,
                                        'sub':    / Allow to subscribe? - Boolean /}
                                    ]
                          }
         }

      You can add custom information to this object. The object will be provided again
      when the client authentication succeeded in :meth:`onAuthenticated`.

      :param authKey: The authentication key.
      :type authKey: str
      :param authExtra: Authentication extra information.
      :type authExtra: dict

      :returns obj or Deferred -- Return a permissions object or None when no permissions granted.
      """
      return None


   def getAuthSecret(self, authKey):
      """
      Get the authentication secret for an authentication key, i.e. the
      user password for the user name. Return None when the authentication
      key does not exist.

      Override in derived class to implement your authentication.

      :param authKey: The authentication key.
      :type authKey: str

      :returns str or Deferred -- The authentication secret for the key or None when the key does not exist.
      """
      return None


   def onAuthTimeout(self):
      """
      Fired when the client does not authenticate itself in time. The default implementation
      will simply fail the connection.

      May be overridden in derived class.
      """
      if not self._clientAuthenticated:
         log.msg("failing connection upon client authentication timeout [%s secs]" % self.clientAuthTimeout)
         self.failConnection()


   def onAuthenticated(self, permissions):
      """
      Fired when client authentication was successful.

      Override in derived class and register PubSub topics and/or RPC endpoints.

      :param permissions: The permissions object returned from :meth:`getAuthPermissions`.
      :type permissions: obj
      """
      pass


   def registerForPubSubFromPermissions(self, permissions):
      """
      Register topics for PubSub from auth permissions.

      :param permissions: The permissions granted to the now authenticated client.
      :type permissions: list
      """
      for p in permissions['pubsub']:
         ## register topics for the clients
         ##
         pubsub = (WampServerProtocol.PUBLISH if p['pub'] else 0) | \
                  (WampServerProtocol.SUBSCRIBE if p['sub'] else 0)
         topic = p['uri']
         if self.pubHandlers.has_key(topic) or self.subHandlers.has_key(topic):
            ## FIXME: handle dups!
            log.msg("DUPLICATE TOPIC PERMISSION !!! " + topic)
         self.registerForPubSub(topic, p['prefix'], pubsub)


   def onSessionOpen(self):
      """
      Called when WAMP session has been established, but not yet authenticated. The default
      implementation will prepare the session allowing the client to authenticate itself.
      """

      ## register RPC endpoints for WAMP-CRA authentication
      ##
      self.registerForRpc(self, WampProtocol.URI_WAMP_PROCEDURE, [WampCraServerProtocol.authRequest,
                                                                  WampCraServerProtocol.auth])

      ## reset authentication state
      ##
      self._clientAuthenticated = False
      self._clientPendingAuth = None
      self._clientAuthTimeoutCall = None

      ## client authentication timeout
      ##
      if self.clientAuthTimeout > 0:
         self._clientAuthTimeoutCall = reactor.callLater(self.clientAuthTimeout, self.onAuthTimeout)


   @exportRpc("authreq")
   def authRequest(self, authKey = None, extra = None):
      """
      RPC endpoint for clients to initiate the authentication handshake.

      :param authKey: Authentication key, such as user name or application name.
      :type authKey: str
      :param extra: Authentication extra information.
      :type extra: dict

      :returns str -- Authentication challenge. The client will need to create an authentication signature from this.
      """

      ## check authentication state
      ##
      if self._clientAuthenticated:
         raise Exception(self.shrink(WampProtocol.URI_WAMP_ERROR + "already-authenticated"), "already authenticated")
      if self._clientPendingAuth is not None:
         raise Exception(self.shrink(WampProtocol.URI_WAMP_ERROR + "authentication-already-requested"), "authentication request already issues - authentication pending")

      ## check authKey
      ##
      if authKey is None and not self.clientAuthAllowAnonymous:
         raise Exception(self.shrink(WampProtocol.URI_WAMP_ERROR + "anyonymous-auth-forbidden"), "authentication as anonymous forbidden")

      if type(authKey) not in [str, unicode, types.NoneType]:
         raise Exception(self.shrink(WampProtocol.URI_WAMP_ERROR + "invalid-argument"), "authentication key must be a string (was %s)" % str(type(authKey)))
      if authKey is not None and self.getAuthSecret(authKey) is None:
         raise Exception(self.shrink(WampProtocol.URI_WAMP_ERROR + "no-such-authkey"), "authentication key '%s' does not exist." % authKey)

      ## check extra
      ##
      if extra:
         if type(extra) != dict:
            raise Exception(self.shrink(WampProtocol.URI_WAMP_ERROR + "invalid-argument"), "extra not a dictionary (was %s)." % str(type(extra)))
      else:
         extra = {}
      #for k in extra:
      #   if type(extra[k]) not in [str, unicode, int, long, float, bool, types.NoneType]:
      #      raise Exception(self.shrink(WampProtocol.URI_WAMP_ERROR + "invalid-argument"), "attribute '%s' in extra not a primitive type (was %s)" % (k, str(type(extra[k]))))

      ## each authentication request gets a unique authid, which can only be used (later) once!
      ##
      authid = newid()

      ## create authentication challenge
      ##
      info = {}
      info['authid'] = authid
      info['authkey'] = authKey
      info['timestamp'] = utcnow()
      info['sessionid'] = self.session_id
      info['extra'] = extra

      pp = maybeDeferred(self.getAuthPermissions, authKey, extra)

      def onAuthPermissionsOk(res):
         if res is None:
            res = {'permissions': {}}
            res['permissions'] = {'pubsub': [], 'rpc': []}
         info['permissions'] = res['permissions']

         if authKey:
            ## authenticated
            ##
            infoser = json.dumps(info)
            sig = self.authSignature(infoser, self.getAuthSecret(authKey))

            self._clientPendingAuth = (info, sig, res)
            return infoser
         else:
            ## anonymous
            ##
            self._clientPendingAuth = (info, None, res)
            return None

      def onAuthPermissionsError(e):
         raise Exception(self.shrink(WampProtocol.URI_WAMP_ERROR + "auth-permissions-error"), str(e))

      pp.addCallbacks(onAuthPermissionsOk, onAuthPermissionsError)

      return pp


   @exportRpc("auth")
   def auth(self, signature = None):
      """
      RPC endpoint for clients to actually authenticate after requesting authentication and computing
      a signature from the authentication challenge.

      :param signature: Authenticatin signature computed by the client.
      :type signature: str

      :returns list -- A list of permissions the client is granted when authentication was successful.
      """

      ## check authentication state
      ##
      if self._clientAuthenticated:
         raise Exception(self.shrink(WampProtocol.URI_WAMP_ERROR + "already-authenticated"), "already authenticated")
      if self._clientPendingAuth is None:
         raise Exception(self.shrink(WampProtocol.URI_WAMP_ERROR + "no-authentication-requested"), "no authentication previously requested")

      ## check signature
      ##
      if type(signature) not in [str, unicode, types.NoneType]:
         raise Exception(self.shrink(WampProtocol.URI_WAMP_ERROR + "invalid-argument"), "signature must be a string or None (was %s)" % str(type(signature)))
      if self._clientPendingAuth[1] != signature:
         ## delete pending authentication, so that no retries are possible. authid is only valid for 1 try!!
         ## FIXME: drop the connection?
         self._clientPendingAuth = None
         raise Exception(self.shrink(WampProtocol.URI_WAMP_ERROR + "invalid-signature"), "signature for authentication request is invalid")

      ## at this point, the client has successfully authenticated!

      ## get the permissions we determined earlier
      ##
      perms = self._clientPendingAuth[2]

      ## delete auth request and mark client as authenticated
      ##
      authKey = self._clientPendingAuth[0]['authkey']
      self._clientAuthenticated = True
      self._clientPendingAuth = None
      if self._clientAuthTimeoutCall is not None:
         self._clientAuthTimeoutCall.cancel()
         self._clientAuthTimeoutCall = None

      ## fire authentication callback
      ##
      self.onAuthenticated(authKey, perms)

      ## return permissions to client
      ##
      return perms['permissions']
