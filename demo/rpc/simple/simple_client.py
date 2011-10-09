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
from autobahn.wamp import WampClientFactory, WampClientProtocol


class SimpleClientProtocol(WampClientProtocol):
   """
   Demonstrates simple Remote Procedure Calls (RPC) with
   Autobahn WebSockets and Twisted Deferreds.
   """

   def show(self, result):
      print "SUCCESS:", result

   def logerror(self, e):
      erroruri, errodesc = e.value.args
      print "ERROR: %s ('%s')" % (erroruri, errodesc)

   def done(self, *args):
      self.sendClose()


   def onOpen(self):

      self.prefix("calc", "http://example.com/simple/calc#")

      d1 = self.call("calc:square", 23).addCallback(self.show)

      d2 = self.call("calc:add", 23, 7).addCallback(self.show)

      d3 = self.call("calc:sum", [1, 2, 3, 4, 5]).addCallback(self.show)

      d4 = self.call("calc:square", 23).addCallback(lambda res: \
                         self.call("calc:sqrt", res)).addCallback(self.show)

      d5 = self.call("calc:sqrt", -1).addCallbacks(self.show, self.logerror)
      d6 = self.call("calc:square", 1001).addCallbacks(self.show, self.logerror)

      d7 = self.call("calc:asum", [1, 2, 3]).addCallback(self.show)
      d8 = self.call("calc:sum", [4, 5, 6]).addCallback(self.show)

      ## we want to shutdown the client exactly when all deferreds are finished
      DeferredList([d1, d2, d3, d4, d5, d6, d7, d8]).addCallback(self.done)


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = WampClientFactory(debug = False)
   factory.protocol = SimpleClientProtocol
   reactor.connectTCP("localhost", 9000, factory)
   reactor.run()
