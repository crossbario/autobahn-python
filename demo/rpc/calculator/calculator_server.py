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

import sys, decimal
from twisted.python import log
from twisted.internet import reactor
from autobahn.websocket import listenWS
from autobahn.wamp import exportRpc, WampServerFactory, WampServerProtocol


class CalculatorServerProtocol(WampServerProtocol):

   def onConnect(self, connectionRequest):
      self.registerForRpc(self, "http://example.com/simple/calculator#")
      self.clear()
      return WampServerProtocol.onConnect(self, connectionRequest)


   def clear(self, arg = None):
      self.op = None
      self.current = decimal.Decimal(0)


   @exportRpc
   def calc(self, arg):

      op = arg["op"]

      if op == "C":
         self.clear()
         return str(self.current)

      num = decimal.Decimal(arg["num"])
      if self.op:
         if self.op == "+":
            self.current += num
         elif self.op == "-":
            self.current -= num
         elif self.op == "*":
            self.current *= num
         elif self.op == "/":
            self.current /= num
         self.op = op
      else:
         self.op = op
         self.current = num

      res = str(self.current)
      if op == "=":
         self.clear()

      return res


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   decimal.getcontext().prec = 20
   factory = WampServerFactory("ws://localhost:9000")
   factory.protocol = CalculatorServerProtocol
   listenWS(factory)
   reactor.run()
