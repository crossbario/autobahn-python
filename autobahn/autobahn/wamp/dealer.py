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

from autobahn import util
from autobahn.wamp import message
from autobahn.wamp.exception import ProtocolError
from autobahn.wamp.interfaces import IDealer



@implementer(IDealer)
class Dealer:
   """
   Basic WAMP dealer, implements :class:`autobahn.wamp.interfaces.IDealer`.
   """

   def __init__(self):
      """
      Constructor.
      """
      ## map: session -> set(registration)
      ## needed for removeSession
      self._session_to_registrations = {}

      ## map: session_id -> session
      ## needed for exclude/eligible
      self._session_id_to_session = {}

      ## map: procedure -> (registration, session)
      self._procs_to_regs = {}

      ## map: registration -> procedure
      self._regs_to_procs = {}

      ## pending callee invocation requests
      self._invocations = {}


   def addSession(self, session):
      """
      Implements :func:`autobahn.wamp.interfaces.IDealer.addSession`
      """
      assert(session not in self._session_to_registrations)

      self._session_to_registrations[session] = set()
      self._session_id_to_session[session._my_session_id] = session


   def removeSession(self, session):
      """
      Implements :func:`autobahn.wamp.interfaces.IDealer.removeSession`
      """
      assert(session in self._session_to_registrations)

      for registration in self._session_to_registrations[session]:
         del self._procs_to_regs[self._regs_to_procs[registration]]
         del self._regs_to_procs[registration]

      del self._session_to_registrations[session]
      del self._session_id_to_session[session._my_session_id]


   def processMessage(self, session, msg):
      """
      Implements :func:`autobahn.wamp.interfaces.IDealer.processMessage`
      """
      assert(session in self._session_to_registrations)

      if isinstance(msg, message.Register):
         self._processRegister(session, msg)

      elif isinstance(msg, message.Unregister):
         self._processUnregister(session, msg)

      elif isinstance(msg, message.Call):
         self._processCall(session, msg)

      elif isinstance(msg, message.Cancel):
         self._processCancel(session, msg)

      elif isinstance(msg, message.Yield):
         self._processYield(session, msg)

      elif isinstance(msg, message.Error) and msg.request_type == message.Invocation.MESSAGE_TYPE:
         self._processInvocationError(session, msg)

      else:
         raise ProtocolError("Unexpected message {}".format(msg.__class__))


   def _processRegister(self, session, register):

      if not register.procedure in self._procs_to_regs:
         registration_id = util.id()
         self._procs_to_regs[register.procedure] = (registration_id, session)
         self._regs_to_procs[registration_id] = register.procedure

         self._session_to_registrations[session].add(registration_id)

         reply = message.Registered(register.request, registration_id)
      else:
         reply = message.Error(message.Register.MESSAGE_TYPE, register.request, 'wamp.error.procedure_already_exists')

      session._transport.send(reply)


   def _processUnregister(self, session, unregister):

      if unregister.registration in self._regs_to_procs:
         del self._procs_to_regs[self._regs_to_procs[unregister.registration]]
         del self._regs_to_procs[unregister.registration]

         self._session_to_registrations[session].discard(unregister.registration)

         reply = message.Unregistered(unregister.request)
      else:
         reply = message.Error(message.Unregister.MESSAGE_TYPE, unregister.request, 'wamp.error.no_such_registration')

      session._transport.send(reply)


   def _processCall(self, session, call):

      if call.procedure in self._procs_to_regs:
         registration_id, endpoint_session = self._procs_to_regs[call.procedure]

         request_id = util.id()

         if call.discloseMe:
            caller = session._my_session_id
         else:
            caller = None

         invocation = message.Invocation(request_id,
                                         registration_id,
                                         args = call.args,
                                         kwargs = call.kwargs,
                                         timeout = call.timeout,
                                         receive_progress = call.receive_progress,
                                         caller = caller)

         self._invocations[request_id] = (call, session)
         endpoint_session._transport.send(invocation)
      else:
         reply = message.Error(message.Call.MESSAGE_TYPE, call.request, 'wamp.error.no_such_procedure')
         session._transport.send(reply)


   def _processCancel(self, session, cancel):

      raise Exception("not implemented")


   def _processYield(self, session, yield_):

      if yield_.request in self._invocations:
         call_msg, call_session = self._invocations[yield_.request]
         msg = message.Result(call_msg.request, args = yield_.args, kwargs = yield_.kwargs, progress = yield_.progress)
         call_session._transport.send(msg)
         if not yield_.progress:
            del self._invocations[yield_.request]
      else:
         raise ProtocolError("Dealer.onYield(): YIELD received for non-pending request ID {}".format(yield_.request))


   def _processInvocationError(self, session, error):

      if error.request in self._invocations:
         call_msg, call_session = self._invocations[error.request]
         msg = message.Error(message.Call.MESSAGE_TYPE, call_msg.request, error.error, args = error.args, kwargs = error.kwargs)
         call_session._transport.send(msg)
         del self._invocations[error.request]
      else:
         raise ProtocolError("Dealer.onInvocationError(): ERROR received for non-pending request_type {} and request ID {}".format(error.request_type, error.request))
