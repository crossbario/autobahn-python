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
from twisted.internet.defer import Deferred, \
                                   DeferredList, \
                                   gatherResults, \
                                   returnValue, \
                                   inlineCallbacks

from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampClientProtocol


class MyClientProtocol(WampClientProtocol):

   def println(self, msg):
      print msg

   @inlineCallbacks
   def onSessionOpen(self):
      self.prefix("calc", "http://example.com/simple/calc#")

      yield self.test1()
      yield self.test2()
      yield self.test3()

      self.sendClose()
      reactor.stop()

   @inlineCallbacks
   def test1(self):
      r = yield self.call("calc:println", "\nStarting test 1 ..\n")
      s = 0
      for i in xrange(10):
         s += yield self.call("calc:sum", range(10))
      print s

   @inlineCallbacks
   def test2(self):
      r = yield self.call("calc:println", "\nStarting test 2 ..\n")
      s = 0
      for i in xrange(10):
         s += yield self.call("calc:asum", range(10))
      print s

   @inlineCallbacks
   def test3(self):
      r = yield self.call("calc:println", "\nStarting test 3 ..\n")
      d = []
      for i in xrange(10):
         d.append(self.call("calc:wsum", range(10)))
      r = yield gatherResults(d).addCallback(lambda l: self.println(sum(l)))


if __name__ == '__main__':
   log.startLogging(sys.stdout)
   factory = WampClientFactory("ws://localhost:9000")
   factory.protocol = MyClientProtocol
   connectWS(factory)
   reactor.run()
