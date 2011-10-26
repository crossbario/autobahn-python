###############################################################################
##
##  Copyright 2011 Tavendo GmbH
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
from twisted.python import log
from twisted.internet.defer import Deferred, maybeDeferred
from websocket import WebSocketProtocol, HttpException
from websocket import WebSocketClientProtocol, WebSocketClientFactory
from websocket import WebSocketServerFactory, WebSocketServerProtocol
from prefixmap import PrefixMap
from util import newid


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
   Base protocol class for Wamp RPC/PubSub.
   """

   MESSAGE_TYPEID_NULL           = 0
   """
   Placeholder for message type of no message.
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


   ERROR_URI_BASE = "http://autobahn.tavendo.de/error#"

   ERROR_URI_GENERIC = ERROR_URI_BASE + "generic"
   ERROR_DESC_GENERIC = "generic error"


   def connectionMade(self):
      self.debug_autobahn = self.factory.debug_autobahn
      self.prefixes = PrefixMap()


   def connectionLost(self, reason):
      pass


   def _protocolError(self, reason):
      if self.debug_autobahn:
         log.msg("Closing Wamp session on protocol violation : %s" % reason)

      ## FIXME: subprotocols are probably not supposed to close with CLOSE_STATUS_CODE_PROTOCOL_ERROR
      ##
      self.protocolViolation("Wamp RPC/PubSub protocol violation ('%s')" % reason)


   def shrink(self, uri):
      """
      Shrink given URI to CURIE according to current prefix mapping.
      If no appropriate prefix mapping is available, return original URI.

      :param uri: URI to shrink.
      :type uri: str
      :returns str -- CURIE or original URI.
      """
      return self.prefixes.shrink(uri)


   def resolve(self, curieOrUri):
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


class WampServerProtocol(WebSocketServerProtocol, WampProtocol):
   """
   Server factory for Wamp RPC/PubSub.
   """

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

      WampProtocol.connectionLost(self, reason)
      WebSocketServerProtocol.connectionLost(self, reason)


   def _getPubHandler(self, topicuri):
      ## Longest matching prefix based resolution of (full) topic URI to
      ## publication handler.
      ## Returns a 5-tuple (consumedUriPart, unconsumedUriPart, handlerObj, handlerProc, prefixMatch)
      ##
      for i in xrange(len(topicuri), -1, -1):
         tt = topicuri[:i]
         if self.pubHandlers.has_key(tt):
            h = self.pubHandlers[tt]
            return (tt, topicuri[i:], h[0], h[1], h[2])
      return None


   def _getSubHandler(self, topicuri):
      ## Longest matching prefix based resolution of (full) topic URI to
      ## subscription handler.
      ## Returns a 5-tuple (consumedUriPart, unconsumedUriPart, handlerObj, handlerProc, prefixMatch)
      ##
      for i in xrange(len(topicuri), -1, -1):
         tt = topicuri[:i]
         if self.subHandlers.has_key(tt):
            h = self.subHandlers[tt]
            return (tt, topicuri[i:], h[0], h[1], h[2])
      return None


   def registerForPubSub(self, topicUri, prefixMatch = False):
      """
      Register a topic URI as publish/subscribe channel in this session.

      :param topicUri: Topic URI to be established as publish/subscribe channel.
      :type topicUri: str
      :param prefixMatch: Allow to match this topic URI by prefix.
      :type prefixMatch: bool
      """
      self.pubHandlers[topicUri] = (None, None, prefixMatch)
      self.subHandlers[topicUri] = (None, None, prefixMatch)
      if self.debug_autobahn:
         log.msg("registered topic %s" % topicUri)


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
      if self.debug_autobahn:
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
      if self.debug_autobahn:
         log.msg("registered publication handler for topic %s" % uri)


   def registerForRpc(self, obj, baseUri = ""):
      """
      Register an service object for RPC. A service object has methods
      which are decorated using @exportRpc.

      :param obj: The object to be registered (in this WebSockets session) for RPC.
      :type obj: Object with methods decorated using @exportRpc.
      :param baseUri: Optional base URI which is prepended to method names for export.
      :type baseUri: String.
      """
      for k in inspect.getmembers(obj.__class__, inspect.ismethod):
         if k[1].__dict__.has_key("_autobahn_rpc_id"):
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
      self.procs[uri] = (obj, proc)
      if self.debug_autobahn:
         log.msg("registered remote procedure on %s" % uri)


   def registerProcedureForRpc(self, uri, proc):
      """
      Register a (free standing) function/procedure for RPC.

      :param uri: URI to register RPC function/procedure under.
      :type uri: str
      :param proc: Free-standing function/procedure.
      :type proc: function/procedure
      """
      self.procs[uri] = (None, proc)
      if self.debug_autobahn:
         log.msg("registered remote procedure on %s" % uri)


   def dispatch(self, topicuri, event, exclude = []):
      """
      Dispatch an event for a topic to all clients subscribed to
      and authorized for that topic. Optionally, exclude list of
      clients.

      :param topicuri: URI of topic to publish event to.
      :type topicuri: str
      :param event: Event to dispatch.
      :type event: obj
      :param exclude: Optional list of clients (protocol instances) to exclude.
      :type exclude: list of obj
      """
      self.factory._dispatchEvent(topicuri, event, exclude)


   def _callProcedure(self, uri, arg = None):
      ## Internal method for calling a procedure invoked via RPC.

      if self.procs.has_key(uri):
         m = self.procs[uri]
         if arg:
            ## method/function called with args
            args = tuple(arg)
            if m[0]:
               ## call object method
               return m[1](m[0], *args)
            else:
               ## call free-standing function/procedure
               return m[1](*args)
         else:
            ## method/function called without args
            if m[0]:
               ## call object method
               return m[1](m[0])
            else:
               ## call free-standing function/procedure
               return m[1]()
      else:
         raise Exception("no procedure %s" % uri)


   def _sendCallResult(self, result, callid):
      ## Internal method for marshaling/sending an RPC success result.

      msg = [WampProtocol.MESSAGE_TYPEID_CALL_RESULT, callid, result]
      try:
         o = json.dumps(msg)
      except:
         raise Exception("call result not JSON serializable")

      self.sendMessage(o)


   def _sendCallError(self, error, callid):
      ## Internal method for marshaling/sending an RPC error result.

      eargs = error.value.args

      if len(eargs) == 0:
         erroruri = WampProtocol.ERROR_URI_GENERIC
         errordesc = WampProtocol.ERROR_DESC_GENERIC
      elif len(eargs) == 1:
         if type(eargs[0]) not in [str, unicode]:
            raise Exception("invalid type for exception description")
         erroruri = WampProtocol.ERROR_URI_GENERIC
         errordesc = eargs[0]
      else:
         if type(eargs[0]) not in [str, unicode]:
            raise Exception("invalid type for exception URI")
         if type(eargs[1]) not in [str, unicode]:
            raise Exception("invalid type for exception description")
         erroruri = eargs[0]
         errordesc = eargs[1]

      msg = [WampProtocol.MESSAGE_TYPEID_CALL_ERROR, callid, self.prefixes.shrink(erroruri), errordesc]
      self.sendMessage(json.dumps(msg))


   def onMessage(self, msg, binary):
      ## Internal method handling Wamp messages received from client.

      if self.debug_autobahn:
         log.msg("WampServerProtocol message received : %s" % str(msg))

      if not binary:
         try:
            obj = json.loads(msg)
            if type(obj) == list:

               ## Call Message
               ##
               if obj[0] == WampProtocol.MESSAGE_TYPEID_CALL:
                  callid = obj[1]
                  procuri = self.prefixes.resolveOrPass(obj[2])
                  arg = obj[3:]
                  d = maybeDeferred(self._callProcedure, procuri, arg)
                  d.addCallback(self._sendCallResult, callid)
                  d.addErrback(self._sendCallError, callid)

               ## Subscribe Message
               ##
               elif obj[0] == WampProtocol.MESSAGE_TYPEID_SUBSCRIBE:
                  topicuri = self.prefixes.resolveOrPass(obj[1])
                  h = self._getSubHandler(topicuri)
                  if h:
                     ## either exact match or prefix match allowed
                     if h[1] == "" or h[4]:

                        ## direct topic
                        if h[2] is None and h[3] is None:
                           self.factory._subscribeClient(self, topicuri)

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
                                 self.factory._subscribeClient(self, topicuri)
                           except:
                              if self.debug_autobahn:
                                 log.msg("execption during topic subscription handler")
                     else:
                        if self.debug_autobahn:
                           log.msg("topic %s matches only by prefix and prefix match disallowed" % topicuri)
                  else:
                     if self.debug_autobahn:
                        log.msg("no topic / subscription handler registered for %s" % topicuri)

               ## Unsubscribe Message
               ##
               elif obj[0] == WampProtocol.MESSAGE_TYPEID_UNSUBSCRIBE:
                  topicuri = self.prefixes.resolveOrPass(obj[1])
                  self.factory._unsubscribeClient(self, topicuri)

               ## Publish Message
               ##
               elif obj[0] == WampProtocol.MESSAGE_TYPEID_PUBLISH:
                  topicuri = self.prefixes.resolveOrPass(obj[1])
                  h = self._getPubHandler(topicuri)
                  if h:
                     ## either exact match or prefix match allowed
                     if h[1] == "" or h[4]:

                        event = obj[2]

                        if len(obj) >= 4:
                           excludeMe = obj[3]
                        else:
                           excludeMe = True

                        if excludeMe:
                           exclude = [self]
                        else:
                           exclude = []

                        ## direct topic
                        if h[2] is None and h[3] is None:
                           self.factory._dispatchEvent(topicuri, event, exclude)

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
                                 self.factory._dispatchEvent(topicuri, e, exclude)
                           except:
                              if self.debug_autobahn:
                                 log.msg("execption during topic publication handler")
                     else:
                        if self.debug_autobahn:
                           log.msg("topic %s matches only by prefix and prefix match disallowed" % topicuri)
                  else:
                     if self.debug_autobahn:
                        log.msg("no topic / publication handler registered for %s" % topicuri)

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
            log.msg("JSON parse error " + str(e))
      else:
         log.msg("binary message")


class WampServerFactory(WebSocketServerFactory):
   """
   Server factory for Wamp RPC/PubSub.
   """

   protocol = WampServerProtocol

   def __init__(self, debug = False, debug_autobahn = False):
      WebSocketServerFactory.__init__(self, debug = debug)
      self.debug_autobahn = debug_autobahn


   def _subscribeClient(self, proto, topicuri):
      ## Internal method called from proto to subscribe client for topic.

      if self.debug_autobahn:
         log.msg("subscribed peer %s for topic %s" % (proto.peerstr, topicuri))

      if not self.subscriptions.has_key(topicuri):
         self.subscriptions[topicuri] = []
      self.subscriptions[topicuri].append(proto)


   def _unsubscribeClient(self, proto, topicuri = None):
      ## Internal method called from proto to unsubscribe client from topic.

      if topicuri:
         if self.subscriptions.has_key(topicuri):
            self.subscriptions[topicuri] = filter(lambda o: o != proto, self.subscriptions[topicuri])
         if self.debug_autobahn:
            log.msg("unsubscribed peer %s from topic %s" % (proto.peerstr, topicuri))
      else:
         for t in self.subscriptions:
            self.subscriptions[t] = filter(lambda o: o != proto, self.subscriptions[t])
         if self.debug_autobahn:
            log.msg("unsubscribed peer %s from all topics" % (proto.peerstr))


   def _dispatchEvent(self, topicuri, event, exclude = []):
      ## Internal method called from proto to publish an received event
      ## to all peers subscribed to the event topic.

      if self.debug_autobahn:
         log.msg("publish event %s for topicuri %s" % (str(event), topicuri))

      if self.subscriptions.has_key(topicuri):
         if len(self.subscriptions[topicuri]) > 0:
            o = [WampProtocol.MESSAGE_TYPEID_EVENT, topicuri, event]
            try:
               msg = json.dumps(o)
               if self.debug_autobahn:
                  log.msg("serialized event msg: " + str(msg))
            except:
               raise Exception("invalid type for event (not JSON serializable)")
            rc = 0
            if len(exclude) > 0:
               recvs = list(set(self.subscriptions[topicuri]) - set(exclude))
            else:
               recvs = self.subscriptions[topicuri]
            for proto in recvs:
               if self.debug_autobahn:
                  log.msg("publish event for topicuri %s to peer %s" % (topicuri, proto.peerstr))
               proto.sendMessage(msg)
               rc += 1
            return rc
      else:
         return 0


   def startFactory(self):
      if self.debug_autobahn:
         log.msg("WampServerFactory starting")
      self.subscriptions = {}


   def stopFactory(self):
      if self.debug_autobahn:
         log.msg("WampServerFactory stopped")


class WampClientProtocol(WebSocketClientProtocol, WampProtocol):
   """
   Client protocol for Wamp RPC/PubSub.
   """

   def connectionMade(self):
      WebSocketClientProtocol.connectionMade(self)
      WampProtocol.connectionMade(self)

      self.calls = {}
      self.subscriptions = {}


   def connectionLost(self, reason):
      WampProtocol.connectionLost(self, reason)
      WebSocketClientProtocol.connectionLost(self, reason)


   def onMessage(self, msg, binary):
      ## Internal method to handle received Wamp messages.

      if binary:
         self._protocolError("binary message received")
         return

      try:
         obj = json.loads(msg)
      except:
         self._protocolError("message payload not valid JSON")
         return

      if type(obj) != list:
         self._protocolError("message payload not a list")
         return

      if len(obj) < 1:
         self._protocolError("message without message type")

      if type(obj[0]) != int:
         self._protocolError("message type not an integer")

      msgtype = obj[0]

      if msgtype not in [WampProtocol.MESSAGE_TYPEID_CALL_RESULT, WampProtocol.MESSAGE_TYPEID_CALL_ERROR, WampProtocol.MESSAGE_TYPEID_EVENT]:
         self._protocolError("invalid message type '%d'" % msgtype)

      if msgtype in [WampProtocol.MESSAGE_TYPEID_CALL_RESULT, WampProtocol.MESSAGE_TYPEID_CALL_ERROR]:
         if len(obj) < 2:
            self._protocolError("call result/error message without callid")
            return
         if type(obj[1]) not in [unicode, str]:
            self._protocolError("invalid type for callid in call result/error message")
            return
         callid = str(obj[1])
         d = self.calls.pop(callid, None)
         if d:
            if msgtype == WampProtocol.MESSAGE_TYPEID_CALL_RESULT:
               if len(obj) != 3:
                  self._protocolError("call result message invalid length")
                  return
               result = obj[2]
               d.callback(result)
            elif msgtype == WampProtocol.MESSAGE_TYPEID_CALL_ERROR:
               if len(obj) != 4:
                  self._protocolError("call error message invalid length")
                  return
               if type(obj[2]) not in [unicode, str]:
                  self._protocolError("invalid type for errorid in call error message")
                  return
               erroruri = str(obj[2])
               if type(obj[3]) not in [unicode, str]:
                  self._protocolError("invalid type for errordesc in call error message")
                  return
               errordesc = str(obj[3])
               e = Exception()
               e.args = (erroruri, errordesc)
               d.errback(e)
            else:
               raise Exception("logic error")
         else:
            if self.debug_autobahn:
               log.msg("callid not found for received call result/error message")
      elif msgtype == WampProtocol.MESSAGE_TYPEID_EVENT:
         if len(obj) != 3:
            self._protocolError("event message invalid length")
            return
         if type(obj[1]) not in [unicode, str]:
            self._protocolError("invalid type for topicid in event message")
            return
         unresolvedTopicUri = str(obj[1])
         topicuri = self.prefixes.resolveOrPass(unresolvedTopicUri)
         if self.subscriptions.has_key(topicuri):
            event = obj[2]
            self.subscriptions[topicuri](topicuri, event)
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


   def publish(self, topicuri, event, excludeMe = True):
      """
      Publish an event under a topic URI. The latter may be abbreviated using a
      CURIE which has been previously defined using prefix(). The event must
      be JSON serializable.

      :param topicuri: The topic URI or CURIE.
      :type topicuri: str
      :param event: Event to be published (must be JSON serializable) or None.
      :type event: value
      :param excludeMe: When True, don't deliver the published event to myself (when I'm subscribed). Default: True.
      :type excludeMe: bool
      """

      if type(topicuri) not in [unicode, str]:
         raise Exception("invalid type for parameter 'topicUri' - must be string (was %s)" % str(type(topicUri)))

      if type(excludeMe) != bool:
         raise Exception("invalid type for parameter 'excludeMe' - must be bool (was %s)" % str(type(excludeMe)))

      msg = [WampProtocol.MESSAGE_TYPEID_PUBLISH, topicuri, event, excludeMe]

      try:
         o = json.dumps(msg)
      except:
         raise Exception("invalid type for parameter 'event' - not JSON serializable")

      self.sendMessage(o)


   def subscribe(self, topicuri, handler):
      """
      Subscribe to topic. When already subscribed, will overwrite the handler.

      :param topicuri: URI or CURIE of topic to subscribe to.
      :type topicuri: str
      :param handler: Event handler to be invoked upon receiving events for topic.
      :type handler: Python callable, will be called as in <callable>(eventUri, event).
      """
      if type(topicuri) not in [unicode, str]:
         raise Exception("invalid type for parameter 'topicUri' - must be string (was %s)" % str(type(topicUri)))

      if type(handler) not in [types.FunctionType, types.MethodType, types.BuiltinFunctionType, types.BuiltinMethodType]:
         raise Exception("invalid type for parameter 'handler' - must be a callable (was %s)" % str(type(handler)))

      turi = self.prefixes.resolveOrPass(topicuri)
      if not self.subscriptions.has_key(turi):
         msg = [WampProtocol.MESSAGE_TYPEID_SUBSCRIBE, topicuri]
         o = json.dumps(msg)
         self.sendMessage(o)
      self.subscriptions[turi] = handler


   def unsubscribe(self, topicuri):
      """
      Unsubscribe from topic. Will do nothing when currently not subscribed to the topic.

      :param topicuri: URI or CURIE of topic to unsubscribe from.
      :type topicuri: str
      """
      if type(topicuri) not in [unicode, str]:
         raise Exception("invalid type for parameter 'topicUri' - must be string (was %s)" % str(type(topicUri)))

      turi = self.prefixes.resolveOrPass(topicuri)
      if self.subscriptions.has_key(turi):
         msg = [WampProtocol.MESSAGE_TYPEID_UNSUBSCRIBE, topicuri]
         o = json.dumps(msg)
         self.sendMessage(o)
         del self.subscriptions[topicuri]


class WampClientFactory(WebSocketClientFactory):
   """
   Client factory for Wamp RPC/PubSub.
   """

   protocol = WampClientProtocol

   def __init__(self, debug = False, debug_autobahn = False):
      WebSocketClientFactory.__init__(self, debug = debug)
      self.debug_autobahn = debug_autobahn
