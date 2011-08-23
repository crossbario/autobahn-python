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
from twisted.internet import reactor, defer
from twisted.python import log
from autobahn.autobahn import AutobahnRpc, AutobahnServerFactory, AutobahnServerProtocol


class SimpleService:

   def __init__(self, label):
      self.setlabel(label)

   @AutobahnRpc
   def getlabel(self):
      return self.label

   @AutobahnRpc
   def setlabel(self, label):
      self.label = "*** " + label + " ***"

   @AutobahnRpc
   def add(self, x, y):
      return x + y

   @AutobahnRpc
   def sub(self, x, y):
      return x - y

   @AutobahnRpc
   def square(self, x):
      return x * x

   @AutobahnRpc
   def sum(self, list):
      return reduce(lambda x, y: x + y, list)

   @AutobahnRpc
   def sqrt(self, x):
      return math.sqrt(x)

   @AutobahnRpc("asum")
   def asyncSum(self, list):
      """
      Simulate a slow function.
      """
      d = defer.Deferred()
      reactor.callLater(3, d.callback, self.sum(list))
      return d


class SimpleServerProtocol(AutobahnServerProtocol):
   """
   Demonstrates creating a server with Autobahn WebSockets that responds
   to RPC calls.
   """

   def onConnect(self, connectionRequest):
      self.svc1 = SimpleService("FooBar")
      self.registerForRpc(self.svc1)


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = AutobahnServerFactory(debug = False)
   factory.protocol = SimpleServerProtocol
   reactor.listenTCP(9000, factory)
   reactor.run()
