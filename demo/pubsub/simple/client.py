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

import sys
from twisted.python import log
from twisted.internet import reactor
from autobahn.wamp import WampClientFactory, WampClientProtocol


class MyClientProtocol(WampClientProtocol):
   """
   Demonstrates simple Publish & Subscribe (PubSub) with Autobahn WebSockets.
   """

   def printEvent(self, topicUri, event):
      print "printEvent", topicUri, event

   def sendSimpleEvent(self):
      self.publish("http://example.com/simple", None)
      reactor.callLater(2, self.sendSimpleEvent)

   def onEvent1(self, topicUri, event):
      self.counter += 1
      self.publish("event:myevent2", {"trigger": event, "counter": self.counter})

   def onOpen(self):

      self.counter = 0
      self.subscribe("http://example.com/simple", self.printEvent)
      self.sendSimpleEvent()

      self.prefix("event", "http://example.com/event#")
      self.subscribe("event:myevent1", self.onEvent1)
      self.subscribe("event:myevent2", self.printEvent)


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = WampClientFactory(debug = False)
   factory.protocol = MyClientProtocol
   reactor.connectTCP("localhost", 9000, factory)
   reactor.run()
