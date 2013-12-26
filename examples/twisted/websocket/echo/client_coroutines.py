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

from autobahn.twisted.websocket import WebSocketClientProtocol, \
                                       WebSocketClientFactory

from twisted.internet.defer import Deferred, inlineCallbacks


def sleep(delay):
   d = Deferred()
   reactor.callLater(delay, d.callback, None)
   return d


class MyClientProtocol(WebSocketClientProtocol):

   def onConnect(self, response):
      print("Server connected: {}".format(response.peer))

   @inlineCallbacks
   def onOpen(self):
      print("WebSocket connection open.")

      ## start sending messages every second ..
      while True:
         self.sendMessage(u"Hello, world!".encode('utf8'))
         self.sendMessage(b"\x00\x01\x03\x04", binary = True)
         yield sleep(1)

   def onMessage(self, payload, isBinary):
      if isBinary:
         print("Binary message received: {} bytes".format(len(payload)))
      else:
         print("Text message received: {}".format(payload.decode('utf8')))

   def onClose(self, wasClean, code, reason):
      print("WebSocket connection closed: {}".format(reason))



if __name__ == '__main__':

   import sys

   from twisted.python import log
   from twisted.internet import reactor

   log.startLogging(sys.stdout)

   factory = WebSocketClientFactory("ws://localhost:9000", debug = False)
   factory.protocol = MyClientProtocol

   reactor.connectTCP("127.0.0.1", 9000, factory)
   reactor.run()
