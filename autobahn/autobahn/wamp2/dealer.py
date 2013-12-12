###############################################################################
##
##  Copyright (C) 2013 Tavendo GmbH
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


import inspect, types

from message import \
   WampMessageProvide,
   WampMessageUnprovide,
   WampMessageCallProgress,
   WampMessageCallResult,
   WampMessageCallError


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



class Endpoint:
   pass


class LocalMethodEndpoint(Endpoint):
   def __init__(self, endpoint, obj, method):
      self.endpoint = endpoint
      self.obj = obj
      self.method = method

   def __call__(self, *args):
      return maybeDeferred(self.method, self.obj, *args)


class LocalProcedureEndpoint(Endpoint):
   def __init__(self, endpoint, proc):
      self.endpoint = endpoint
      self.proc = proc

   def __call__(self, *args):
      return maybeDeferred(self.proc, *args)


class RemoteEndpoint(Endpoint):
   def __init__(self, endpoint, proto):
      self.endpoint = endpoint
      self.proto = proto

   def __call__(self, *args):
      return self.proto.call(self.endpoint, *args)



class Dealer:

   def __init__(self):
      self._protos = set()
      self._endpoints = {}
      self._dealers = set()

   def add(self, proto):
      pass

   def remove(self, proto):
      pass

   def addDealer(self, proto):
      print "addDealer"
      assert(proto not in self._dealers)
      self._dealers.add(proto)

      for endpoint in self._endpoints:
         msg = WampMessageProvide(endpoint)
         bytes, isbinary = proto.factory._serializer.serialize(msg)
         proto.sendMessage(bytes, isbinary)


   def removeDealer(self, proto):
      assert(proto in self._dealers)
      self._dealers.remove(proto)

   def onCall(self, proto, call):

      if self._endpoints.has_key(call.endpoint):

         endpoint = self._endpoints[call.endpoint]

         cargs = tuple(call.args)

         def onSuccess(res):
            msg = WampMessageCallResult(call.callid, res)
            bytes, isbinary = proto.factory._serializer.serialize(msg)
            proto.sendMessage(bytes, isbinary)

         def onError(err):
            print err

         d = endpoint(*cargs)
         d.addCallbacks(onSuccess, onError)

      else:
         print "FOOOOOOOOOOO"


   def onCancelCall(self, proto, call):
      pass

   def onProvide(self, proto, provide):
      self._endpoints[provide.endpoint] = RemoteEndpoint(provide.endpoint, proto)

      for dealer_proto in self._dealers:
         if dealer_proto != proto:
            bytes, isbinary = dealer_proto.factory._serializer.serialize(provide)
            dealer_proto.sendMessage(bytes, isbinary)


   def onUnprovide(self, proto, unprovide):
      pass


   def _announceEndpoint(self, endpoint):
      msg = WampMessageProvide(endpoint)
      for dealer in self._dealers:
         bytes, isbinary = dealer.factory._serializer.serialize(msg)
         dealer.sendMessage(bytes, isbinary)


   def register(self, endpoint, obj):
      for k in inspect.getmembers(obj.__class__, inspect.ismethod):
         if k[1].__dict__.has_key("_autobahn_rpc_id"):
            fq_endpoint = endpoint + k[1].__dict__["_autobahn_rpc_id"]
            method = k[1]
            self.registerMethod(fq_endpoint, obj, method)


   def registerMethod(self, endpoint, obj, method):
      self._endpoints[endpoint] = LocalMethodEndpoint(endpoint, obj, method)
      self._announceEndpoint(endpoint)


   def registerProcedure(self, endpoint, procedure):
      self._endpoints[endpoint] = LocalProcedureEndpoint(endpoint, procedure)
      self._announceEndpoint(endpoint)

