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
from functools import partial
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList, returnValue, inlineCallbacks
from twisted.python import log
from autobahn.autobahn import AutobahnClientFactory, AutobahnClientProtocol


class SimpleClientProtocol(AutobahnClientProtocol):
   """
   Demonstrates simple Remote Procedure Calls (RPC) with
   Autobahn WebSockets and Twisted Deferreds.
   """

   def show(self, result):
      print "SUCCESS:", result

   def alert(self, result):
      print "ERROR:", result

   def close(self, *args):
      self.sendClose()


   def onOpen(self):

      ## run all tests (tests return a Twisted Deferred)
      tests = []
      tests.append(self.testBasicRpc())
      tests.append(self.testHandleRpcErrors())
      tests.append(self.testChainedRpc())
      tests.append(self.testInlineCallbacks())

      ## close when all tests have finished
      DeferredList(tests).addCallback(self.close)


   def testBasicRpc(self):
      """
      Demonstrates basic RPC with Autobahn Websockets.
      """

      d1 = self.call("getlabel").addCallback(self.show)

      d2 = self.call("square", 23).addCallback(self.show)

      d3 = self.call("add", 5, 3).addCallback(self.show)

      d4 = self.call("sum", [1, 2, 3, 4, 5]).addCallback(self.show)

      d5 = self.call("asum", [1, 2, 3, 4, 5]).addCallback(self.show)

      return DeferredList([d1, d2, d3, d4, d5])


   def testHandleRpcErrors(self):
      """
      Demonstrates use of success/error handlers.
      """

      d1 = self.call("no_such_method").addCallbacks(self.show, self.alert)

      d2 = self.call("sqrt", 36).addCallbacks(self.show, self.alert)

      d3 = self.call("sqrt", -1).addCallbacks(self.show, self.alert)

      return DeferredList([d1, d2])


   def testChainedRpc(self):
      """
      Demonstrates the chaining of Deferreds, in particular with
      Autobahn WebSockets RPC.

      See also these references:

      http://twistedmatrix.com/documents/current/core/howto/defer.html
      http://mithrandi.net/blog/2011/06/flow-control-with-deferreds-by-example
      """

      # Non-chained : prints 31
      d1 = self.call("sub", 6**2, 5).addCallback(self.show)

      # Option 1 : prints 31
      d2 = self.call("square", 6).addCallback(lambda res: self.call("sub", res, 5)).addCallback(self.show)

      # Option 2 : prints 31
      d3 = self.call("square", 6).addCallback(self.rcall, "sub", 5).addCallback(self.show)

      # Option 3 : prints -31
      d4 = self.call("square", 6).addCallback(partial(self.call, "sub", 5)).addCallback(self.show)

      # more "realistic" example:
      d5 = self.call("setlabel", "MooMoo").addCallback(self.rcall, "getlabel").addCallback(self.show)

      return DeferredList([d1, d2, d3, d4, d5])


   def testInlineCallbacks(self):
      """
      Demonstrates the use of the inline callbacks pattern with Twisted Deferreds
      and Autobahn WebSockets RPC.
      """
      return self.myfun(42).addCallback(self.show)


   @inlineCallbacks
   def myfun(self, val):

      print "myfun:1", val

      r = yield self.mysubfun(val)
      print "myfun:2", r

      returnValue(r * 10)


   @inlineCallbacks
   def mysubfun(self, val):

      print "mysubfun:1", val

      r1 = yield self.call("asum", [1, 2, 3, val])
      print "mysubfun:2", r1

      r2 = yield self.call("square", r1)
      print "mysubfun:3", r2

      returnValue(r2 + 1)


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = AutobahnClientFactory(debug = False)
   factory.protocol = SimpleClientProtocol
   reactor.connectTCP("localhost", 9000, factory)
   reactor.run()
