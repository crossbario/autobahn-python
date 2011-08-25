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
from websocket import WebSocketClientProtocol, WebSocketClientFactory, WebSocketServerFactory, WebSocketServerProtocol, HttpException
from qnamemap import QnameMap


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
   Client-to-server message establishing a URI prefix to be used in QNames.
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


   ERROR_DEFAULT_URI = "http://autobahn/ontology/error/generic"
   ERROR_DEFAULT_DESCRIPTION = "generic error"


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
            self._registerProcedure(uri, obj, proc)


   def _registerProcedure(self, uri, obj, proc):
      ## Internal method for registering a procedure for RPC.

      self.procs[uri] = (obj, proc)
      if self.debug:
         log.msg("registered procedure on %s" % uri)


   def _callProcedure(self, uri, arg = None):
      ## Internal method for calling a procedure invoked via RPC.

      if self.procs.has_key(uri):
         m = self.procs[uri]
         if arg:
            args = tuple(arg)
            return m[1](m[0], *args)
         else:
            return m[1](m[0])
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
         erroruri = AutobahnProtocol.ERROR_DEFAULT_URI
         errordesc = AutobahnProtocol.ERROR_DEFAULT_DESCRIPTION
      elif len(eargs) == 1:
         if type(eargs[0]) not in [str, unicode]:
            raise Exception("invalid type for exception description")
         erroruri = AutobahnProtocol.ERROR_DEFAULT_URI
         errordesc = eargs[0]
      else:
         if type(eargs[0]) not in [str, unicode]:
            raise Exception("invalid type for exception URI")
         if type(eargs[1]) not in [str, unicode]:
            raise Exception("invalid type for exception description")
         erroruri = eargs[0]
         errordesc = eargs[1]

      msg = [AutobahnProtocol.MESSAGE_TYPEID_CALL_ERROR, callid, erroruri, errordesc]
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
                  procuri = obj[1]
                  callid = obj[2]
                  arg = obj[3:]
                  d = maybeDeferred(self._callProcedure, procuri, arg)
                  d.addCallback(self._sendCallResult, callid)
                  d.addErrback(self._sendCallError, callid)

               ## Subscribe Message
               ##
               elif obj[0] == AutobahnProtocol.MESSAGE_TYPEID_SUBSCRIBE:
                  topic = obj[1]
                  self.factory.subscribe(self, topic)

               ## Unsubscribe Message
               ##
               elif obj[0] == AutobahnProtocol.MESSAGE_TYPEID_UNSUBSCRIBE:
                  pass

               ## Publish Message
               ##
               elif obj[0] == AutobahnProtocol.MESSAGE_TYPEID_PUBLISH:
                  topic = obj[1]
                  event = obj[2]
                  self.factory.publish(topic, event)

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

   def subscribe(self, proto, topic):
      ## Internal method called from proto to subscribe client for topic.

      if self.debug:
         log.msg("subscribed peer %s for topic %s" % (proto.peerstr, topic))

      if not self.subscriptions.has_key(topic):
         self.subscriptions[topic] = []
      self.subscriptions[topic].append(proto)


   def publish(self, topic, event):
      ## Internal method called from proto to publish an received event
      ## to all peers subscribed to the event topic.

      if self.debug:
         log.msg("publish event %s for topic %s" % (str(event), topic))

      if self.subscriptions.has_key(topic):
         if len(self.subscriptions[topic]) > 0:
            eventObj = ["EVENT", topic, event]
            eventJson = json.dumps(eventObj)
            for proto in self.subscriptions[topic]:
               proto.sendMessage(eventJson)
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
      self.qnames = QnameMap()


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
            if len(obj) != 3:
               self._protocolError("call result/error message invalid length")
               return
            if msgtype == AutobahnProtocol.MESSAGE_TYPEID_CALL_RESULT:
               result = obj[2]
               d.callback(result)
            elif msgtype == AutobahnProtocol.MESSAGE_TYPEID_CALL_ERROR:
               if type(obj[2]) not in [unicode, str]:
                  self._protocolError("invalid type for errorid in call error message")
                  return
               erroruri = str(obj[2])
               d.errback(erroruri)
            else:
               raise Exception("logic error")
         else:
            if self.debug:
               log.msg("callid not found for received call result/error message")
      elif msgtype == AutobahnProtocol.MESSAGE_TYPEID_EVENT:
         pass
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
      Establishes a prefix to be used in QNames instead of URIs having that
      prefix for both client-to-server and server-to-client messages.

      :param prefix: Prefix used in Qnames.
      :type prefix: str
      :param uri: URI (partial) that this prefix will resolve to.
      :type uri: str
      """

      if type(prefix) != str:
         raise Exception("invalid type for prefix")

      if type(uri) not in [unicode, str]:
         raise Exception("invalid type for URI")

      if self.qnames.get(prefix):
         raise Exception("prefix already defined")

      self.qnames.set(prefix, uri)

      msg = [AutobahnProtocol.MESSAGE_TYPEID_PREFIX, prefix, uri]

      self.sendMessage(json.dumps(msg))


   def publish(self, topicuri, event):
      """
      Publish an event under a topic URI. The latter may be abbreviated using a
      Qname which has been previously defined using prefix(). The event must
      be JSON serializable.

      :param topicuri: The topic URI or Qname.
      :type topicuri: str
      :param event: Event to be published (can be anything JSON serializable) or None.
      :type  event: value
      """

      if type(topicuri) not in [unicode, str]:
         raise Exception("invalid type for URI")

      if QnameMap.isQname(topicuri):
         if not self.qnames.resolve(topicuri):
            raise Exception("undefined qname used")

      msg = [AutobahnProtocol.MESSAGE_TYPEID_PUBLISH, topicuri, event]

      try:
         o = json.dumps(msg)
      except:
         raise Exception("event argument not JSON serializable")

      self.sendMessage(o)



class AutobahnClientFactory(WebSocketClientFactory):
   """
   Client factory for Autobahn RPC/PubSub.
   """

   protocol = AutobahnClientProtocol
