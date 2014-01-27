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
from autobahn.wamp.interfaces import IBroker



@implementer(IBroker)
class Broker:
   """
   Basic WAMP broker, implements :class:`autobahn.wamp.interfaces.IBroker`.
   """

   def __init__(self):
      """
      Constructor.
      """
      self._sessions = set()
      self._session_id_to_session = {}

      self._subscribers = {}


   def addSession(self, session):
      """
      Implements :func:`autobahn.wamp.interfaces.IBroker.addSession`
      """
      assert(session not in self._sessions)

      self._sessions.add(session)
      self._session_id_to_session[session._my_session_id] = session


   def removeSession(self, session):
      """
      Implements :func:`autobahn.wamp.interfaces.IBroker.removeSession`
      """
      assert(session in self._sessions)

      self._sessions.remove(session)
      del self._session_id_to_session[session._my_session_id]

      for subscriptionid, subscribers in self._subscribers.values():
         subscribers.discard(session)


   def processMessage(self, session, msg):
      """
      Implements :func:`autobahn.wamp.interfaces.IBroker.processMessage`
      """
      assert(session in self._sessions)

      if isinstance(msg, message.Publish):
         self._processPublish(session, msg)

      elif isinstance(msg, message.Subscribe):
         self._processSubscribe(session, msg)

      elif isinstance(msg, message.Unsubscribe):
         self._processUnsubscribe(session, msg)

      else:
         raise ProtocolError("Unexpected message {}".format(msg.__class__))


   def _processPublish(self, session, publish):

      if self._subscribers.has_key(publish.topic) and self._subscribers[publish.topic]:

         ## initial list of receivers are all subscribers ..
         ##
         subscription_id, receivers = self._subscribers[publish.topic]

         ## filter by "eligible" receivers
         ##
         if publish.eligible:
            eligible = []
            for s in publish.eligible:
               if s in self._session_id_to_session:
                  eligible.append(self._session_id_to_session[s])
            if eligible:
               receivers = set(eligible) & receivers

         ## remove "excluded" receivers
         ##
         if publish.exclude:
            exclude = []
            for s in publish.exclude:
               if s in self._session_id_to_session:
                  exclude.append(self._session_id_to_session[s])
            if exclude:
               receivers = receivers - set(exclude)

         ## remove publisher
         ##
         if publish.excludeMe is None or not publish.excludeMe:
            if session in receivers:
               receivers.remove(session)

      else:
         receivers = []

      publication_id = util.id()

      ## send publish acknowledge when requested
      ##
      if publish.acknowledge:
         msg = message.Published(publish.request, publication_id)
         session._transport.send(msg)

      ## if receivers is non-empty, dispatch event ..
      ##
      if receivers:
         if publish.discloseMe:
            publisher = session._my_session_id
         else:
            publisher = None
         msg = message.Event(subscription_id,
                             publication_id,
                             args = publish.args,
                             kwargs = publish.kwargs,
                             publisher = publisher)
         for session in receivers:
            session._transport.send(msg)


   def _processSubscribe(self, session, subscribe):

      if not self._subscribers.has_key(subscribe.topic):
         subscription_id = util.id()
         self._subscribers[subscribe.topic] = (subscription_id, set())

      subscription_id, subscribers = self._subscribers[subscribe.topic]

      if not session in subscribers:
         subscribers.add(session)

      reply = message.Subscribed(subscribe.request, subscription_id)
      session._transport.send(reply)


   def _processUnsubscribe(self, session, unsubscribe):
      assert(session in self._sessions)

      # if self._subscribers.has_key(unsubscribe.topic):
      #    if proto in self._subscribers[unsubscribe.topic]:
      #       self._subscribers[unsubscribe.topic].discard(proto)
