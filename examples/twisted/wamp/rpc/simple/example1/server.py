###############################################################################
##
##  Copyright (C) 2011-2013 Tavendo GmbH
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
from twisted.internet import reactor, defer
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import listenWS
from autobahn.wamp import exportRpc, \
                          WampServerFactory, \
                          WampServerProtocol


def multiply(x, y):
   """
   A free standing procedure that we remote.
   """
   return x * y


class RpcServer1Protocol(WampServerProtocol):
   """
   A minimalistic RPC server.
   """

   def onSessionOpen(self):
      ## When the WAMP session has been established, register callables
      ## to be remoted (made available for RPC)
      ##
      self.registerProcedureForRpc("http://example.com/simple/calc#mul", multiply)
      self.registerMethodForRpc("http://example.com/simple/calc#sub", self, RpcServer1Protocol.doSub)
      self.registerForRpc(self, "http://example.com/simple/calc#")

   @exportRpc("add")
   def doAdd(self, x, y):
      """
      A method that we remote by using the exportRpc decorator.
      """
      return x + y

   def doSub(self, x, y):
      """
      A method that we remote explicitly.
      """
      return x - y



if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   factory = WampServerFactory("ws://localhost:9000", debugWamp = debug)
   factory.protocol = RpcServer1Protocol
   factory.setProtocolOptions(allowHixie76 = True)
   listenWS(factory)

   webdir = File(".")
   web = Site(webdir)
   reactor.listenTCP(8080, web)

   reactor.run()
