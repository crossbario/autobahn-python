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

from twisted.python import log

from autobahn.wamp import role
from autobahn.wamp import message
from autobahn.wamp.exception import ProtocolError
from autobahn.wamp.broker import Broker
from autobahn.wamp.dealer import Dealer
from autobahn.wamp.interfaces import IRouter, IRouterFactory


@implementer(IRouter)
class Router:
   """
   Basic WAMP router.

   This class implements :class:`autobahn.wamp.interfaces.IRouter`.
   """

   def __init__(self, factory, realm):
      self.factory = factory
      self.realm = realm
      self._broker = Broker(realm)
      self._dealer = Dealer(realm)
      self._attached = 0


   def attach(self, session):
      """
      Implements :func:`autobahn.wamp.interfaces.IRouter.attach`
      """
      self._broker.attach(session)
      self._dealer.attach(session)
      self._attached += 1

      return [self._broker._role_features, self._dealer._role_features]


   def detach(self, session):
      """
      Implements :func:`autobahn.wamp.interfaces.IRouter.detach`
      """
      self._broker.detach(session)
      self._dealer.detach(session)
      self._attached -= 1
      if not self._attached:
         self.factory.onLastDetach(self)


   def process(self, session, msg):
      """
      Implements :func:`autobahn.wamp.interfaces.IRouter.process`
      """
      ## Broker
      ##
      if isinstance(msg, message.Publish):
         self._broker.processPublish(session, msg)

      elif isinstance(msg, message.Subscribe):
         self._broker.processSubscribe(session, msg)

      elif isinstance(msg, message.Unsubscribe):
         self._broker.processUnsubscribe(session, msg)

      ## Dealer
      ##
      elif isinstance(msg, message.Register):
         self._dealer.processRegister(session, msg)

      elif isinstance(msg, message.Unregister):
         self._dealer.processUnregister(session, msg)

      elif isinstance(msg, message.Call):
         self._dealer.processCall(session, msg)

      elif isinstance(msg, message.Cancel):
         self._dealer.processCancel(session, msg)

      elif isinstance(msg, message.Yield):
         self._dealer.processYield(session, msg)

      elif isinstance(msg, message.Error) and msg.request_type == message.Invocation.MESSAGE_TYPE:
         self._dealer.processInvocationError(session, msg)

      else:
         raise ProtocolError("Unexpected message {}".format(msg.__class__))



@implementer(IRouterFactory)
class RouterFactory:
   """
   Basic WAMP Router factory.

   This class implements :class:`autobahn.wamp.interfaces.IRouterFactory`.
   """

   def __init__(self, debug = False):
      self._routers = {}
      self.debug = debug


   def get(self, realm):
      """
      Implements :func:`autobahn.wamp.interfaces.IRouterFactory.get`
      """
      if not realm in self._routers:
         self._routers[realm] = Router(self, realm)
         if self.debug:
            log.msg("Router created for realm '{}'".format(realm))
      return self._routers[realm]


   def onLastDetach(self, router):
      assert(router.realm in self._routers)
      del self._routers[router.realm]
      if self.debug:
         log.msg("Router destroyed for realm '{}'".format(router.realm))
