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

import sys, math
from twisted.python import log
from twisted.internet import reactor, defer
from autobahn.websocket import listenWS
from autobahn.wamp import exportSub, exportPub, WampServerFactory, WampServerProtocol


class MyTopicService:

   def __init__(self, allowedTopicIds):
      self.allowedTopicIds = allowedTopicIds
      self.serial = 0


   @exportSub("foobar", True)
   def subscribe(self, topicUriPrefix, topicUriSuffix):
      """
      Custom topic subscription handler.
      """
      print "client wants to subscribe to %s%s" % (topicUriPrefix, topicUriSuffix)
      try:
         i = int(topicUriSuffix)
         if i in self.allowedTopicIds:
            print "Subscribing client to topic Foobar %d" % i
            return True
         else:
            print "Client not allowed to subscribe to topic Foobar %d" % i
            return False
      except:
         print "illegal topic - skipped subscription"
         return False


   @exportPub("foobar", True)
   def publish(self, topicUriPrefix, topicUriSuffix, event):
      """
      Custom topic publication handler.
      """
      print "client wants to publish to %s%s" % (topicUriPrefix, topicUriSuffix)
      try:
         i = int(topicUriSuffix)
         if type(event) == dict and event.has_key("count"):
            if event["count"] > 0:
               self.serial += 1
               event["serial"] = self.serial
               print "ok, published enriched event"
               return event
            else:
               print "event count attribute is negative"
               return None
         else:
            print "event is not dict or misses count attribute"
            return None
      except:
         print "illegal topic - skipped publication of event"
         return None


class MyServerProtocol(WampServerProtocol):

   def onSessionOpen(self):

      ## register a single, fixed URI as PubSub topic
      self.registerForPubSub("http://example.com/event/simple")

      ## register a URI and all URIs having the string as prefix as PubSub topic
      #self.registerForPubSub("http://example.com/event/simple", True)

      ## register any URI (string) as topic
      #self.registerForPubSub("", True)

      ## register a topic handler to control topic subscriptions/publications
      self.topicservice = MyTopicService([1, 3, 7])
      self.registerHandlerForPubSub(self.topicservice, "http://example.com/event/")


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = WampServerFactory("ws://localhost:9000", debugWamp = True)
   factory.protocol = MyServerProtocol
   listenWS(factory)
   reactor.run()
