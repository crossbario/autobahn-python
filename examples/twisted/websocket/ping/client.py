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

from twisted.internet import reactor
from twisted.python import log

from autobahn.twisted.websocket import WebSocketClientFactory, \
                                       WebSocketClientProtocol, \
                                       connectWS


class PingClientProtocol(WebSocketClientProtocol):

   def onOpen(self):
      self.pingsReceived = 0
      self.pongsSent = 0

   def onClose(self, wasClean, code, reason):
      reactor.stop()

   def onPing(self, payload):
      self.pingsReceived += 1
      print("Ping received from {} - {}".format(self.peer, self.pingsReceived))
      self.sendPong(payload)
      self.pongsSent += 1
      print("Pong sent to {} - {}".format(self.peer, self.pongsSent))



if __name__ == '__main__':

   log.startLogging(sys.stdout)

   if len(sys.argv) < 2:
      print("Need the WebSocket server address, i.e. ws://localhost:9000")
      sys.exit(1)

   factory = WebSocketClientFactory(sys.argv[1], debug = 'debug' in sys.argv)
   factory.protocol = PingClientProtocol
   connectWS(factory)

   reactor.run()
