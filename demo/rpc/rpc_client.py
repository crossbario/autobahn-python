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

import json
from twisted.internet import reactor, defer
from autobahn.websocket import WebSocketClientFactory, WebSocketClientProtocol
from autobahn.autobahn import AutobahnClientProtocol


class RpcClientProtocol(AutobahnClientProtocol):

   def show(self, notice):
      print notice

   def delay(self, _, delay, fun):
      reactor.callLater(delay, fun)

   def show(self, res, notice = None):
      self.i += 1
      self.l.append(self.i)
      if notice:
         print notice, res
      else:
         print res

   def doit(self):
      d = self.call(self.i, "square").addCallback(self.show)
      d.addCallback(self.delay, 1, self.doit)
 #     d.addCallback(reactor.callLater, 5, reactor.stop)
      #self.call([1, 2, 3], "sum").addCallback(self.show)

   def doit2(self, _ = None):
      d = self.call(range(0, self.i), "asyncSum").addCallback(self.show).addCallback(self.doit2)

   @defer.inlineCallbacks
   def doit3(self):
      print "doit3"
      res1 = yield self.call([1, 2, 3], "asyncSum")
      print "doit3 res1", res1
      res2 = yield self.call(res1, "square")
      print "doit3 res2", res2
      defer.returnValue(res2 + 1)
      #self.sendClose()

   @defer.inlineCallbacks
   def doit4(self):
      r = yield self.doit3()
      print "doit4", r
      defer.returnValue(r + 1)

   def onOpen(self):
      self.i = 1
      self.l = [self.i]
      #res.addCallback(self.show)
      #res.addErrback(self.show)
      #self.call([1, 2, 3], "asyncSum").addCallback(self.show)
      #self.call([1, 2, 3], "sum").addCallback(self.call, procid = "square").addCallback(self.show, "final result =").addCallback(self.sendClose)
      #d = self.call([4, 5, 6, "kjh"], "sum")
      #d.addCallback(self.show, "success : ")
      #d.addErrback(self.show, "failure : ")
      #d.addBoth(self.sendClose)
      #self.step1()
      #self.call([1, 2, 3], "sum").addCallback(lambda x: x + 50).addCallback(self.show).addCallback(self.sendClose)
      #self.doit2()
      self.doit4().addCallback(self.show, "result1 =")
      self.call([4, 5, 6], "sum").addCallback(self.show, "result2 =")


   def step1(self):
      d = self.call([1, 2, 3], "sum")
      d.addCallback(self.step2)

   def step2(self, res):
      print res
      self.call(res + 50, "square").addCallback(self.show).addCallback(self.sendClose)





if __name__ == '__main__':

   factory = WebSocketClientFactory()
   factory.protocol = RpcClientProtocol
   reactor.connectTCP("localhost", 9000, factory)
   reactor.run()
