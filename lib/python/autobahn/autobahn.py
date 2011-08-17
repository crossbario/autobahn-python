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
from twisted.internet import defer
from websocket import WebSocketClientProtocol, WebSocketClientFactory, WebSocketServerFactory, WebSocketServerProtocol, HttpException

def newId():
   return ''.join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_") for i in range(16)])


def rpc(arg = None):
   ## @rcp decorator without argument
   if type(arg) is types.FunctionType:
      arg._autobahn_rpc_id = arg.__name__
      return arg
   ## @rpc decorator with argument
   else:
      def inner(f):
         f._autobahn_rpc_id = arg
         return f
      return inner


class AutobahnServerProtocol(WebSocketServerProtocol):

   def callResult(self, res, callId):
      self.sendMessage(json.dumps(["CALL_RESULT", callId, res]))

   def callError(self, res, callId):
#      self.sendMessage(json.dumps(["CALL_ERROR", callId, res.getErrorMessage()]))
      self.sendMessage(json.dumps(["CALL_ERROR", callId, str(res.value)]))

   def onMessage(self, msg, binary):
      if not binary:
         try:
            obj = json.loads(msg)
            if type(obj) == list and len(obj) == 4:
               if type(obj[0]) == unicode and type(obj[1]) == unicode and type(obj[2]) == unicode:
                  if obj[0] == "CALL":
                     procId = obj[1]
                     callId = obj[2]
                     arg = obj[3]
                     d = defer.maybeDeferred(self.factory.callProcedure, procId, arg)
                     d.addCallback(self.callResult, callId)
                     d.addErrback(self.callError, callId)
                        #res = self.factory.callProcedure(procId, arg)
                        #self.sendMessage(json.dumps(res))
#                     except e:
#                        print "error " + str(e)
                  else:
                     log.msg("unknown message type")
               else:
                  log.msg("invalid type")
                  print obj
            else:
               log.msg("msg not a list")
         except:
            log.msg("JSON parse error")
      else:
         log.msg("binary message")


class AutobahnServerFactory(WebSocketServerFactory):

   protocol = AutobahnServerProtocol

   def __init__(self, debug = False):
      self.debug = debug
      self.procs = {}
      for k in inspect.getmembers(self.__class__, inspect.ismethod):
         if k[1].__dict__.has_key("_autobahn_rpc_id"):
            #uri = self.__class__.BASEURI + k[1].__dict__["uri"]
            uri = k[1].__dict__["_autobahn_rpc_id"]
            proc = k[1]
            self.registerProcedure(uri, proc)

   def startFactory(self):
      pass

   def stopFactory(self):
      pass

   def registerProcedure(self, uri, proc):
      self.procs[uri] = proc
      print "registered procedure", proc, "on", uri

   def callProcedure(self, uri, arg):
      if self.procs.has_key(uri):
         return self.procs[uri](self, arg)
      else:
         raise Exception("no procedure %s" % uri)


class AutobahnClientProtocol(WebSocketClientProtocol):

   def __init__(self, debug = False):
      WebSocketClientProtocol.__init__(self, debug)
      self.calls = {}

   def call(self, arg, procid):
      callid = newId()
      d = defer.Deferred()
      self.calls[callid] = d
      msg = json.dumps(["CALL", procid, callid, arg])
      self.sendMessage(msg)
      return d

   def onMessage(self, msg, binary):
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
