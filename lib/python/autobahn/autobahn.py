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


def exportRpc(arg = None):
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


class AutobahnProtocol:

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


   def _newid(self):
      return ''.join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_") for i in range(16)])


   def _protocolError(self, reason):
      if self.debug:
         log.msg("Closing Autobahn session on protocol violation : %s" % reason)
      #self.failConnection()
      self.sendClose(WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, "Autobahn RPC/PubSub protocol violation ('%s')" % reason)


class AutobahnServerProtocol(WebSocketServerProtocol, AutobahnProtocol):
   """
   Server factory for Autobahn RPC/PubSub.
   """

   def __init__(self, debug = False):
      self.debug = debug
      self.procs = {}
      self.prefixes = PrefixMap()


   def connectionLost(self, reason):
      WebSocketServerProtocol.connectionLost(self, reason)
      self.factory._unsubscribeClient(self)


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
      if self.debug:
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
      if self.debug:
         log.msg("registered remote procedure on %s" % uri)


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

      msg = [AutobahnProtocol.MESSAGE_TYPEID_CALL_RESULT, callid, result]
      try:
         o = json.dumps(msg)
      except:
         raise Exception("call result not JSON serializable")

      self.sendMessage(o)


   def _sendCallError(self, error, callid):
      ## Internal method for marshaling/sending an RPC error result.

      eargs = error.value.args

      if len(eargs) == 0:
         erroruri = AutobahnProtocol.ERROR_URI_GENERIC
         errordesc = AutobahnProtocol.ERROR_DESC_GENERIC
      elif len(eargs) == 1:
         if type(eargs[0]) not in [str, unicode]:
            raise Exception("invalid type for exception description")
         erroruri = AutobahnProtocol.ERROR_URI_GENERIC
         errordesc = eargs[0]
      else:
         if type(eargs[0]) not in [str, unicode]:
            raise Exception("invalid type for exception URI")
         if type(eargs[1]) not in [str, unicode]:
            raise Exception("invalid type for exception description")
         erroruri = eargs[0]
         errordesc = eargs[1]

      msg = [AutobahnProtocol.MESSAGE_TYPEID_CALL_ERROR, callid, self.prefixes.shrink(erroruri), errordesc]
      self.sendMessage(json.dumps(msg))


   def onMessage(self, msg, binary):
      ## Internal method handling Autobahn messages received from client.

      if self.debug:
         log.msg("AutobahnServerProtocol message received : %s" % str(msg))

      if not binary:
         try:
            obj = json.loads(msg)
            if type(obj) == list:

               ## Call Message
               ##
               if obj[0] == AutobahnProtocol.MESSAGE_TYPEID_CALL:
                  callid = obj[1]
                  procuri = self.prefixes.resolveOrPass(obj[2])
                  arg = obj[3:]
                  d = maybeDeferred(self._callProcedure, procuri, arg)
                  d.addCallback(self._sendCallResult, callid)
                  d.addErrback(self._sendCallError, callid)

               ## Subscribe Message
               ##
               elif obj[0] == AutobahnProtocol.MESSAGE_TYPEID_SUBSCRIBE:
                  topicuri = self.prefixes.resolveOrPass(obj[1])
                  self.factory._subscribeClient(self, topicuri)

               ## Unsubscribe Message
               ##
               elif obj[0] == AutobahnProtocol.MESSAGE_TYPEID_UNSUBSCRIBE:
                  topicuri = self.prefixes.resolveOrPass(obj[1])
                  self.factory._unsubscribeClient(self, topicuri)

               ## Publish Message
               ##
               elif obj[0] == AutobahnProtocol.MESSAGE_TYPEID_PUBLISH:
                  topicuri = self.prefixes.resolveOrPass(obj[1])
                  event = obj[2]
                  self.factory._dispatchEvent(topicuri, event)

               ## Define prefix to be used in CURIEs
               ##
               elif obj[0] == AutobahnProtocol.MESSAGE_TYPEID_PREFIX:
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


class AutobahnServerFactory(WebSocketServerFactory):
   """
   Server factory for Autobahn RPC/PubSub.
   """

   protocol = AutobahnServerProtocol

   def _subscribeClient(self, proto, topicuri):
      ## Internal method called from proto to subscribe client for topic.

      if self.debug:
         log.msg("subscribed peer %s for topic %s" % (proto.peerstr, topicuri))

      if not self.subscriptions.has_key(topicuri):
         self.subscriptions[topicuri] = []
      self.subscriptions[topicuri].append(proto)


   def _unsubscribeClient(self, proto, topicuri = None):
      ## Internal method called from proto to unsubscribe client from topic.

      if topicuri:
         if self.subscriptions.has_key(topicuri):
            self.subscriptions[topicuri] = filter(lambda o: o != proto, self.subscriptions[topicuri])
         if self.debug:
            log.msg("unsubscribed peer %s from topic %s" % (proto.peerstr, topicuri))
      else:
         for t in self.subscriptions:
            self.subscriptions[t] = filter(lambda o: o != proto, self.subscriptions[t])
         if self.debug:
            log.msg("unsubscribed peer %s from all topics" % (proto.peerstr))


   def _dispatchEvent(self, topicuri, event):
      ## Internal method called from proto to publish an received event
      ## to all peers subscribed to the event topic.

      if self.debug:
         log.msg("publish event %s for topicuri %s" % (str(event), topicuri))

      if self.subscriptions.has_key(topicuri):
         if len(self.subscriptions[topicuri]) > 0:
            o = [AutobahnProtocol.MESSAGE_TYPEID_EVENT, topicuri, event]
            try:
               msg = json.dumps(o)
            except:
               raise Exception("invalid type for event (not JSON serializable)")
            for proto in self.subscriptions[topicuri]:
               proto.sendMessage(msg)
      else:
         pass


   def startFactory(self):
      if self.debug:
         log.msg("AutobahnServerFactory starting")
      self.subscriptions = {}


   def stopFactory(self):
      if self.debug:
         log.msg("AutobahnServerFactory stopped")


class AutobahnClientProtocol(WebSocketClientProtocol, AutobahnProtocol):
   """
   Client protocol for Autobahn RPC/PubSub.
   """

   def __init__(self, debug = False):

      WebSocketClientProtocol.__init__(self, debug)
      self.calls = {}
      self.subscriptions = {}
      self.prefixes = PrefixMap()


   def onMessage(self, msg, binary):
      ## Internal method to handle received Autobahn messages.

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

      if msgtype not in [AutobahnProtocol.MESSAGE_TYPEID_CALL_RESULT, AutobahnProtocol.MESSAGE_TYPEID_CALL_ERROR, AutobahnProtocol.MESSAGE_TYPEID_EVENT]:
         self._protocolError("invalid message type '%d'" % msgtype)

      if msgtype in [AutobahnProtocol.MESSAGE_TYPEID_CALL_RESULT, AutobahnProtocol.MESSAGE_TYPEID_CALL_ERROR]:
         if len(obj) < 2:
            self._protocolError("call result/error message without callid")
            return
         if type(obj[1]) not in [unicode, str]:
            self._protocolError("invalid type for callid in call result/error message")
            return
         callid = str(obj[1])
         d = self.calls.pop(callid, None)
         if d:
            if msgtype == AutobahnProtocol.MESSAGE_TYPEID_CALL_RESULT:
               if len(obj) != 3:
                  self._protocolError("call result message invalid length")
                  return
               result = obj[2]
               d.callback(result)
            elif msgtype == AutobahnProtocol.MESSAGE_TYPEID_CALL_ERROR:
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
            if self.debug:
               log.msg("callid not found for received call result/error message")
      elif msgtype == AutobahnProtocol.MESSAGE_TYPEID_EVENT:
         if len(obj) != 3:
            self._protocolError("event message invalid length")
            return
         if type(obj[1]) not in [unicode, str]:
            self._protocolError("invalid type for topicid in event message")
            return
         topicuri = self.prefixes.resolveOrPass(obj[1])
         event = obj[2]
         cur_d = self.subscriptions[topicuri]
         new_d = Deferred()
         self.subscriptions[topicuri] = new_d
         cur_d.callback([event, new_d])
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
         callid = self._newid()
         if not self.calls.has_key(callid):
            break
      d = Deferred()
      self.calls[callid] = d
      msg = [AutobahnProtocol.MESSAGE_TYPEID_CALL, callid, procuri]
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

      msg = [AutobahnProtocol.MESSAGE_TYPEID_PREFIX, prefix, uri]

      self.sendMessage(json.dumps(msg))


   def publish(self, topicuri, event):
      """
      Publish an event under a topic URI. The latter may be abbreviated using a
      CURIE which has been previously defined using prefix(). The event must
      be JSON serializable.

      :param topicuri: The topic URI or CURIE.
      :type topicuri: str
      :param event: Event to be published (must be JSON serializable) or None.
      :type event: value
      """

      if type(topicuri) not in [unicode, str]:
         raise Exception("invalid type for URI")

      msg = [AutobahnProtocol.MESSAGE_TYPEID_PUBLISH, topicuri, event]

      try:
         o = json.dumps(msg)
      except:
         raise Exception("event argument not JSON serializable")

      self.sendMessage(o)


   def subscribe(self, topicuri):
      """
      Subscribe to topic.

      :param topicuri: URI or CURIE of topic to subscribe to.
      :type topicuri: str
      """
      d = Deferred()
      self.subscriptions[topicuri] = d
      msg = [AutobahnProtocol.MESSAGE_TYPEID_SUBSCRIBE, topicuri]
      o = json.dumps(msg)
      self.sendMessage(o)
      return d


   def unsubscribe(self, topicuri):
      """
      Unsubscribe from topic.

      :param topicuri: URI or CURIE of topic to unsubscribe from.
      :type topicuri: str
      """
      del self.subscriptions[topicuri]
      msg = [AutobahnProtocol.MESSAGE_TYPEID_UNSUBSCRIBE, topicuri]
      o = json.dumps(msg)
      self.sendMessage(o)
      return d


class AutobahnClientFactory(WebSocketClientFactory):
   """
   Client factory for Autobahn RPC/PubSub.
   """

   protocol = AutobahnClientProtocol
