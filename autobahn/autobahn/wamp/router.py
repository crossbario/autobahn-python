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

from autobahn.wamp import message
from autobahn.wamp.exception import ProtocolError
from autobahn.wamp.broker import Broker
from autobahn.wamp.dealer import Dealer
from autobahn.wamp.interfaces import IRouter



@implementer(IRouter)
class Router:
   """
   Basic WAMP router.

   This class implements

    - :class:`autobahn.wamp.interfaces.IBroker`
    - :class:`autobahn.wamp.interfaces.IDealer`    
   """

   def __init__(self, realm):
      self._realm = realm
      self._broker = Broker()
      self._dealer = Dealer()


   def addSession(self, session):
      self._broker.addSession(session)
      self._dealer.addSession(session)


   def removeSession(self, session):
      self._broker.removeSession(session)
      self._dealer.removeSession(session)


   def processMessage(self, session, msg):
      """
      Implements :func:`autobahn.wamp.interfaces.IDealer.processMessage`
      """
      ## Broker
      ##
      if isinstance(msg, message.Publish):
         self._broker._processPublish(session, msg)

      elif isinstance(msg, message.Subscribe):
         self._broker._processSubscribe(session, msg)

      elif isinstance(msg, message.Unsubscribe):
         self._broker._processUnsubscribe(session, msg)

      ## Dealer
      ##
      elif isinstance(msg, message.Register):
         self._dealer._processRegister(session, msg)

      elif isinstance(msg, message.Unregister):
         self._dealer._processUnregister(session, msg)

      elif isinstance(msg, message.Call):
         self._dealer._processCall(session, msg)

      elif isinstance(msg, message.Cancel):
         self._dealer._processCancel(session, msg)

      elif isinstance(msg, message.Yield):
         self._dealer._processYield(session, msg)

      elif isinstance(msg, message.Error) and msg.request_type == message.Invocation.MESSAGE_TYPE:
         self._dealer._processInvocationError(session, msg)

      else:
         raise ProtocolError("Unexpected message {}".format(msg.__class__))



class RouterFactory:

   def __init__(self):
      self._routers = {}


   def get(self, realm):
      if not realm in self._routers:
         self._routers[realm] = Router(realm)
         print("Router created for realm '{}'".format(realm))
      return self._routers[realm]
