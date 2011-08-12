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

from ranstring import randomByteString
from twisted.internet import reactor
from autobahn.websocket import WebSocketProtocol, WebSocketClientFactory, WebSocketClientProtocol

FRAME_SIZE = 1 * 2**20


class FrameBasedHashClientProtocol(WebSocketClientProtocol):
   """
   Message-based WebSockets client that generates stream of random octets
   sent to streaming WebSockets server in one message. The server will
   respond to us with the SHA-256 computed over message payload. When
   we receive response, we repeat.
   """

   def sendOneFrame(self):
      """
      Send out a WebSockets binary message with random bytes.
      """
      data = randomByteString(FRAME_SIZE)
      self.beginMessageFrame(FRAME_SIZE)
      self.sendMessageFrameData(data)

   def onOpen(self):
      self.scount = 0
      self.stopped = False
      self.beginMessage(opcode = WebSocketProtocol.MESSAGE_TYPE_BINARY)
      self.sendOneFrame()

   def onMessage(self, msg, binary):
      print "Digest for message %d computed by server: %s" % (self.scount, msg)
      self.scount += 1

      if not self.stopped:
         if self.scount > 5:
            self.endMessage()
            self.sendClose()
            self.stopped = True
         else:
            self.sendOneFrame()


if __name__ == '__main__':

   factory = WebSocketClientFactory()
   factory.protocol = FrameBasedHashClientProtocol
   reactor.connectTCP("localhost", 9000, factory)
   reactor.run()
