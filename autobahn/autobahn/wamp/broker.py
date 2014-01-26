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


from autobahn import util
from autobahn.wamp import message


class Broker:

   def __init__(self):
      ## FIXME: maintain 2 maps: topic => protos (subscribers), proto => topics
      self._brokers = set()
      self._sessions = set()
      self._session_id_to_session = {}
      self._subscribers = {}


   def addBroker(self, session):
      """
      Add upstream broker session.
      """
      print "Broker.addBroker", session
      assert(session not in self._brokers)
      self._brokers.add(session)


   def removeBroker(self, session):
      print "Broker.removeBroker", session
      assert(session in self._brokers)
      self._brokers.remove(session)


   def addSession(self, session):
      """
      Add downstream consumer session.
      """
      print "Broker.addSession", session
      assert(session not in self._sessions)

      self._sessions.add(session)
      self._session_id_to_session[session._my_session_id] = session


   def removeSession(self, session):
      print "Broker.removeSession", session
      assert(session in self._sessions)

      self._sessions.remove(session)
      del self._session_id_to_session[session._my_session_id]

      for subscriptionid, subscribers in self._subscribers.values():
         subscribers.discard(session)


   def onPublish(self, session, publish):
      """
      Publish from downstream consumer session.
      """
      print "Broker.onPublish", session, publish
      assert(session in self._sessions)

      for broker_session in self._brokers:
         if broker_session != session:
            broker_session._transport.send(publish)

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


   def onSubscribe(self, session, subscribe):
      print "Broker.onSubscribe", session, subscribe
      assert(session in self._sessions)

      if not self._subscribers.has_key(subscribe.topic):
         subscription_id = util.id()
         self._subscribers[subscribe.topic] = (subscription_id, set())

      subscription_id, subscribers = self._subscribers[subscribe.topic]

      if not session in subscribers:
         subscribers.add(session)

      reply = message.Subscribed(subscribe.request, subscription_id)
      session._transport.send(reply)


   def onUnsubscribe(self, session, unsubscribe):
      assert(session in self._sessions)

      # if self._subscribers.has_key(unsubscribe.topic):
      #    if proto in self._subscribers[unsubscribe.topic]:
      #       self._subscribers[unsubscribe.topic].discard(proto)
