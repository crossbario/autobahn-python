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
from twisted.internet import reactor, defer
from twisted.python import log
from autobahn.autobahn import AutobahnClientFactory, AutobahnClientProtocol


class SimpleClientProtocol(AutobahnClientProtocol):
   """
   Demonstrates the use of the inline callbacks pattern with Twisted Deferreds
   and Autobahn WebSockets.
   """

   @defer.inlineCallbacks
   def mysubfun(self, val):
      print "mysubfun:1", val
      r1 = yield self.call([1, 2, 3, val], "asum")
      print "mysubfun:2", r1
      r2 = yield self.call(r1, "square")
      print "mysubfun:3", r2
      defer.returnValue(r2 + 1)


   @defer.inlineCallbacks
   def myfun(self, val):
      print "myfun:1", val
      r = yield self.mysubfun(val)
      print "myfun:2", r
      defer.returnValue(r * 10)


   def show(self, result):
      print "SUCCESS:", result


   def onOpen(self):
      self.myfun(42).addCallback(self.show).addCallback(self.sendClose)


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = AutobahnClientFactory(debug = False)
   factory.protocol = SimpleClientProtocol
   reactor.connectTCP("localhost", 9000, factory)
   reactor.run()
