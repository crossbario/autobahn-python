###############################################################################
##
##  Copyright 2011,2012 Tavendo GmbH
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

from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, \
                          WampClientProtocol


class PubSubClient1(WampClientProtocol):

   def onSessionOpen(self):
      self.subscribe("http://example.com/simple", self.onSimpleEvent)
      self.sendSimpleEvent()

   def onSimpleEvent(self, topicUri, event):
      print "Event", topicUri, event

   def sendSimpleEvent(self):
      self.publish("http://example.com/simple", "Hello!")
      reactor.callLater(2, self.sendSimpleEvent)


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'

   factory = WampClientFactory("ws://localhost:9000", debugWamp = debug)
   factory.protocol = PubSubClient1

   connectWS(factory)

   reactor.run()
