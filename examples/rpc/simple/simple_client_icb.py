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
from twisted.internet.defer import Deferred, returnValue, inlineCallbacks
from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampClientProtocol


class SimpleClientProtocol(WampClientProtocol):
   """
   Demonstrates simple Remote Procedure Calls (RPC) with
   Autobahn WebSockets and Twisted Inline Callbacks.
   """

   def show(self, result):
      print "SUCCESS:", result

   def done(self, *args):
      self.sendClose()


   def onSessionOpen(self):

      self.prefix("calc", "http://example.com/simple/calc#")

      self.myfun(42).addCallback(self.show).addCallback(self.done)


   @inlineCallbacks
   def myfun(self, val):

      print "myfun:1", val

      r = yield self.mysubfun(val)
      print "myfun:2", r

      returnValue(r * 10)


   @inlineCallbacks
   def mysubfun(self, val):

      print "mysubfun:1", val

      r1 = yield self.call("calc:asum", [1, 2, 3, val])
      print "mysubfun:2", r1

      r2 = yield self.call("calc:square", r1)
      print "mysubfun:3", r2

      returnValue(r2 + 1)


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = WampClientFactory("ws://localhost:9000")
   factory.protocol = SimpleClientProtocol
   connectWS(factory)
   reactor.run()
