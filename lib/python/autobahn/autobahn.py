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

def newId():
   return ''.join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_") for i in range(16)])


def AutobahnRpc(arg = None):
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


class AutobahnServerProtocol(WebSocketServerProtocol):

   def __init__(self, debug = False):
      self.debug = debug
      self.procs = {}

   def registerForRpc(self, obj, baseUri = ""):
      for k in inspect.getmembers(obj.__class__, inspect.ismethod):
         if k[1].__dict__.has_key("_autobahn_rpc_id"):
            uri = baseUri + k[1].__dict__["_autobahn_rpc_id"]
            proc = k[1]
            self.registerProcedure(uri, obj, proc)

   def registerProcedure(self, uri, obj, proc):
      self.procs[uri] = (obj, proc)
      print "registered procedure", obj, proc, "on", uri

   def callProcedure(self, uri, arg = None):
      if self.procs.has_key(uri):
         m = self.procs[uri]
         if arg:
            args = tuple(arg)
            return m[1](m[0], *args)
         else:
            return m[1](m[0])
      else:
         raise Exception("no procedure %s" % uri)

   def callResult(self, res, callId):
      self.sendMessage(json.dumps(["CALL_RESULT", callId, res]))

   def callError(self, res, callId):
#      self.sendMessage(json.dumps(["CALL_ERROR", callId, res.getErrorMessage()]))
      self.sendMessage(json.dumps(["CALL_ERROR", callId, str(res.value)]))

   def onMessage(self, msg, binary):
      if not binary:
         try:
            obj = json.loads(msg)
            if type(obj) == list:
               if obj[0] == "CALL":
                  procId = obj[1]
                  callId = obj[2]
                  arg = obj[3:]
                  d = maybeDeferred(self.callProcedure, procId, arg)
                  d.addCallback(self.callResult, callId)
                  d.addErrback(self.callError, callId)
               elif obj[0] == "SUBSCRIBE":
                  eventId = obj[1]
                  self.factory.subscribe(self, eventId)
               elif obj[0] == "PUBLISH":
                  eventId = obj[1]
                  event = obj[2]
                  self.factory.onEvent(eventId, event)
               else:
                  log.msg("unknown message type")
            else:
               log.msg("msg not a list")
         except Exception, e:
            log.msg("JSON parse error " + str(e))
      else:
         log.msg("binary message")


class AutobahnServerFactory(WebSocketServerFactory):

   protocol = AutobahnServerProtocol

   def subscribe(self, proto, eventId):
      print "AutobahnServerFactory.subscribe", proto, eventId
      if not self.subscriptions.has_key(eventId):
         self.subscriptions[eventId] = []
      self.subscriptions[eventId].append(proto)

   def onEvent(self, eventId, event):
      #print "AutobahnServerFactory.onEvent", eventId, event
      if self.subscriptions.has_key(eventId):
         if len(self.subscriptions[eventId]) > 0:
            eventObj = ["EVENT", eventId, event]
            eventJson = json.dumps(eventObj)
            for proto in self.subscriptions[eventId]:
               proto.sendMessage(eventJson)
      else:
         pass

   def startFactory(self):
      self.subscriptions = {}

   def stopFactory(self):
      pass


class AutobahnClientProtocol(WebSocketClientProtocol):

   def __init__(self, debug = False):

      WebSocketClientProtocol.__init__(self, debug)
      self.calls = {}


   def onMessage(self, msg, binary):

      ## handle received Autobahn messages:
      ## Call Results and Published Events
      obj = json.loads(msg)
      msg_type = obj[0]
      callid = obj[1]
      res = obj[2]
      d = self.calls.pop(callid, None)
      if d:
         if msg_type == "CALL_RESULT":
            d.callback(res)
         elif msg_type == "CALL_ERROR":
            d.errback(res)
         else:
            pass


   def call(self, *args):
      """
      Perform a remote-procedure call (RPC). The first argument is the procedure
      ID (mandatory). Subsequent positional arguments can be provided (must be
      JSON serializable). The return value is a Twisted Deferred.
      """

      procid = args[0]
      callid = newId()
      d = Deferred()
      self.calls[callid] = d
      a = ["CALL", procid, callid]
      a.extend(args[1:])
      msg = json.dumps(a)
      self.sendMessage(msg)
      return d


   def rcall(self, *args):
      """
      Similar to call(), can be used for less verbose chaining of RPC calls (see
      tutorial for details).

      The second argument is the procedure ID (mandatory). The first argument can
      be either None, in which case the RPC has no argument, or not None, in which
      case it is the first positional RPC argument. Any arguments args[2:] can
      provide further positional arguments to the RPC.
      """

      a = []
      a.append(args[1]) # procedure ID
      if args[0]:
         a.append(args[0]) # result from previous deferred
         a.extend(args[2:]) # new args
      return self.call(*a)


class AutobahnClientFactory(WebSocketClientFactory):
   pass
