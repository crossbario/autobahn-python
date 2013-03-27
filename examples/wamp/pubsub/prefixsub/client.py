###############################################################################
##
##  Copyright 2013 Tavendo GmbH
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

from autobahn.util import newid
from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, \
                          WampClientProtocol


class PubSubClient1(WampClientProtocol):

   def onSessionOpen(self):
      ## subscribe to all topics with URIs having the given prefix
      #self.subscribe("http://example.com/event#", self.onMyEvent)
      #self.subscribe("http://example.com/event#", self.onMyEvent, match = 'prefix')
      self.subscribe("^http://.*/foobar$", self.onMyEvent, match = 'regex')
      self.sendMyEvent()

   def onMyEvent(self, topicUri, event):
      print "Event", topicUri, event

   def sendMyEvent(self):
      self.publish("http://example.com/event#%s" % newid(), "Hello 1")
      self.publish("http://example.com/foobar", "Hello 2")
      self.publish("http://example.com/foobar/baz", "Hello 3")
      reactor.callLater(2, self.sendMyEvent)


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'

   factory = WampClientFactory("ws://localhost:9000", debugWamp = debug)
   factory.protocol = PubSubClient1

   connectWS(factory)

   reactor.run()
