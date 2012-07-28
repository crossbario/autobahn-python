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
from twisted.internet.defer import Deferred, DeferredList
from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampClientProtocol


class MyClientProtocol(WampClientProtocol):
   """
   Demonstrates simple Publish & Subscribe (PubSub) with Autobahn WebSockets.
   """

   def show(self, result):
      print "SUCCESS:", result

   def logerror(self, e):
      erroruri, errodesc = e.value.args
      print "ERROR: %s ('%s')" % (erroruri, errodesc)

   def done(self, *args):
      self.sendClose()

   def onFoobar(self, topicUri, event):
      print "FOOBAR", topicUri, event

   def onSessionOpen(self):

      self.prefix("event", "http://resource.example.com/schema/event#")

      self.subscribe("event:foobar", self.onFoobar)

      self.publish("event:foobar", {"name": "foo", "value": "bar", "num": 666})
      self.publish("event:foobar", {"name": "foo", "value": "bar", "num": 666})
      self.publish("event:foobar-extended", {"name": "foo", "value": "bar", "num": 42})
      self.publish("event:foobar-limited", {"name": "foo", "value": "bar", "num": 23})

      #self.done()


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = WampClientFactory("ws://localhost:9000")
   factory.protocol = MyClientProtocol
   connectWS(factory)
   reactor.run()
