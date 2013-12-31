###############################################################################
##
##  Copyright 2011,2012 Tavendo GmbH
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

from twisted.python import log
from twisted.internet import reactor, defer
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import listenWS
from autobahn.wamp import exportRpc, \
                          WampServerFactory, \
                          WampServerProtocol


class Calc:
   """
   A simple calc service we will export for Remote Procedure Calls (RPC).

   All you need to do is use the @exportRpc decorator on methods
   you want to provide for RPC and register a class instance in the
   server factory (see below).

   The method will be exported under the Python method name, or
   under the (optional) name you can provide as an argument to the
   decorator (see asyncSum()).
   """

   @exportRpc
   def add(self, x, y):
      return x + y

   @exportRpc
   def sub(self, x, y):
      return x - y

   @exportRpc
   def square(self, x):
      MAX = 1000
      if x > MAX:
         ## raise a custom exception
         raise Exception("http://example.com/error#number_too_big",
                         "%d too big for me, max is %d" % (x, MAX),
                         MAX)
      return x * x

   @exportRpc
   def sum(self, list):
      return reduce(lambda x, y: x + y, list)

   @exportRpc
   def pickySum(self, list):
      errs = []
      for i in list:
         if i % 3 == 0:
            errs.append(i)
      if len(errs) > 0:
         raise Exception("http://example.com/error#invalid_numbers",
                         "one or more numbers are multiples of 3",
                         errs)
      return reduce(lambda x, y: x + y, list)

   @exportRpc
   def sqrt(self, x):
      return math.sqrt(x)

   @exportRpc("asum")
   def asyncSum(self, list):
      ## Simulate a slow function.
      d = defer.Deferred()
      reactor.callLater(3, d.callback, self.sum(list))
      return d


class SimpleServerProtocol(WampServerProtocol):
   """
   Demonstrates creating a simple server with Autobahn WebSockets that
   responds to RPC calls.
   """

   def onSessionOpen(self):

      # when connection is established, we create our
      # service instances ...
      self.calc = Calc()

      # .. and register them for RPC. that's it.
      self.registerForRpc(self.calc, "http://example.com/simple/calc#")


if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   factory = WampServerFactory("ws://localhost:9000", debugWamp = debug)
   factory.protocol = SimpleServerProtocol
   factory.setProtocolOptions(allowHixie76 = True)
   listenWS(factory)

   webdir = File(".")
   web = Site(webdir)
   reactor.listenTCP(8080, web)

   reactor.run()
