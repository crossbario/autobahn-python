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


## incoming client connections
## incoming broker connections
## outgoing broker connections

from autobahn import util
from autobahn.wamp import message


class BrokerOld:

   def __init__(self):
      ## FIXME: maintain 2 maps: topic => protos (subscribers), proto => topics
      self._protos = set()
      self._subscribers = {}
      self._brokers = set()

   def addBroker(self, proto):
      assert(proto not in self._brokers)
      self._brokers.add(proto)

      # def on_publish(topic, event):

      # for topic in self._subscribers:
      #    proto.subscribe()
      #    msg = WampMessageEvent(publish.topic, publish.event)
      #    bytes, isbinary = proto.factory._serializer.serialize(msg)
      #    for proto in receivers:
      #       proto.sendMessage(bytes, isbinary)


   def removeBroker(self, proto):
      assert(proto in self._brokers)
      self._brokers.remove(proto)

   def add(self, proto):
      assert(proto not in self._protos)
      self._protos.add(proto)

   def remove(self, proto):
      assert(proto in self._protos)
      self._protos.remove(proto)
      for subscriptionid, subscribers in self._subscribers.values():
         subscribers.discard(proto)


   def onPublish(self, proto, publish):
      assert(proto in self._protos)

      for broker_proto in self._brokers:
         if broker_proto != proto:
            bytes, isbinary = broker_proto._serializer.serialize(publish)
            broker_proto.sendMessage(bytes, isbinary)

      if self._subscribers.has_key(publish.topic):
         subscriptionid, receivers = self._subscribers[publish.topic]
         if len(receivers) > 0:
            msg = WampMessageEvent(subscriptionid, publish.topic, publish.event)
            for proto in receivers:
               bytes, isbinary = proto._serializer.serialize(msg)
               proto.sendMessage(bytes, isbinary)


   def onSubscribe(self, proto, subscribe):
      assert(proto in self._protos)

      # if subscribe.topic.startswith("http://example.com/"):
      #    proto.sendWampMessage(WampMessageSubscribeError(subscribe.subscribeid, "http://api.wamp.ws/error#forbidden"))
      #    return


      if not self._subscribers.has_key(subscribe.topic):
         subscriptionid = newid()
         self._subscribers[subscribe.topic] = (subscriptionid, set())

      subscriptionid, subscribers = self._subscribers[subscribe.topic]

      if not proto in subscribers:
         subscribers.add(proto)

      proto.sendWampMessage(WampMessageSubscription(subscribe.subscribeid, subscriptionid))


   def onPublish2(self, proto, publish):
      assert(proto in self._protos)

      for broker_proto in self._brokers:
         if broker_proto != proto:
            bytes, isbinary = broker_proto._serializer.serialize(publish)
            broker_proto.sendMessage(bytes, isbinary)

      if self._subscribers.has_key(publish.topic):
         receivers = self._subscribers[publish.topic]
         if len(receivers) > 0:
            msg = WampMessageEvent(publish.topic, publish.event)
            bytes, isbinary = proto._serializer.serialize(msg)
            for proto in receivers:
               proto.sendMessage(bytes, isbinary)


   def onSubscribe2(self, proto, subscribe):
      assert(proto in self._protos)

      if not self._subscribers.has_key(subscribe.topic):
         self._subscribers[subscribe.topic] = set()

      if not proto in self._subscribers[subscribe.topic]:
         self._subscribers[subscribe.topic].add(proto)


   def onUnsubscribe(self, proto, unsubscribe):
      assert(proto in self._protos)

      if self._subscribers.has_key(unsubscribe.topic):
         if proto in self._subscribers[unsubscribe.topic]:
            self._subscribers[unsubscribe.topic].discard(proto)


class Broker:

   def __init__(self):
      ## FIXME: maintain 2 maps: topic => protos (subscribers), proto => topics
      self._brokers = set()
      self._sessions = set()
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


   def removeSession(self, session):
      print "Broker.removeSession", session
      assert(session in self._sessions)
      self._sessions.remove(session)
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

      if self._subscribers.has_key(publish.topic):
         subscription_id, receivers = self._subscribers[publish.topic]
         if len(receivers) > 0:
            publication_id = util.id()
            msg = message.Event(subscription_id, publication_id, args = publish.args, kwargs = publish.kwargs)
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



   def publish(self, topic, *args, **kwargs):
      """
      Direct publish.
      
      Implements :func:`autobahn.wamp.interfaces.IPublisher.publish`
      """


   def onMessage(self, session, msg):
      print "Broker.onMessage", msg
