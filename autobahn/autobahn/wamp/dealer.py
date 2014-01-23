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



class DealerOld:

   def __init__(self):
      self._protos = set()
      self._endpoints = {}
      self._dealers = set()

   def add(self, proto):
      pass

   def remove(self, proto):
      pass

   def addDealer(self, proto):
      print("addDealer")
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
            print(err)

         d = endpoint(*cargs)
         d.addCallbacks(onSuccess, onError)

      else:
         print("FOOOOOOOOOOO")


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



from autobahn import util
from autobahn.wamp import message


class Dealer:
   def __init__(self):
      self._procs_to_regs = {}
      self._regs_to_procs = {}
      self._invocations = {}

   def addSession(self, session):
      print "Dealer.addSession", session

   def removeSession(self, session):
      print "Dealer.removeSession", session


   def onRegister(self, session, register):
      print "Dealer.onRegister", session , register
      assert(isinstance(register, message.Register))

      if not register.procedure in self._procs_to_regs:
         registration_id = util.id()
         self._procs_to_regs[register.procedure] = (registration_id, session)
         self._regs_to_procs[registration_id] = register.procedure
         reply = message.Registered(register.request, registration_id)
      else:
         reply = message.Error(call.request, 'wamp.error.procedure_already_exists')

      session._transport.send(reply)


   def onUnregister(self, session, unregister):
      print "Dealer.onUnregister", session , unregister
      assert(isinstance(unregister, message.Unregister))

      if unregister.registration in self._regs_to_procs:
         del self._procs_to_regs[self._regs_to_procs[unregister.registration]]
         del self._regs_to_procs[unregister.registration]
         reply = message.Unregistered(unregister.request)
      else:
         reply = message.Error(unregister.request, 'wamp.error.no_such_registration')

      session._transport.send(reply)


   def onCall(self, session, call):
      print "Dealer.onCall", session , call
      assert(isinstance(call, message.Call))

      if call.procedure in self._procs_to_regs:
         registration_id, endpoint_session = self._procs_to_regs[call.procedure]
         request_id = util.id()
         invocation = message.Invocation(request_id, registration_id, args = call.args, kwargs = call.kwargs)
         self._invocations[request_id] = (call.request, session)
         endpoint_session._transport.send(invocation)
      else:
         reply = message.Error(call.request, 'wamp.error.no_such_procedure')
         session._transport.send(reply)


   def onCancel(self, session, cancel):
      print "Dealer.onCancel", session , cancel
      raise Exception("not implemented")


   def onYield(self, session, yield_):
      print "Dealer.onYield", session , yield_
      assert(isinstance(yield_, message.Yield))

      if yield_.request in self._invocations:
         call_request_id, call_session = self._invocations[yield_.request]
         result_msg = message.Result(call_request_id, args = yield_.args, kwargs = yield_.kwargs)
         call_session._transport.send(result_msg)
