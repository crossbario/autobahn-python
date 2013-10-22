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
from zope.interface import implements
from twisted.internet import reactor, interfaces
from autobahn.websocket import WebSocketProtocol, \
                               WebSocketClientFactory, \
                               WebSocketClientProtocol, \
                               connectWS

BATCH_SIZE = 1 * 2**20


class StreamingHashClientProtocol(WebSocketClientProtocol):
   """
   Streaming WebSockets client that generates stream of random octets
   sent to WebSockets server as a sequence of batches in one frame, in
   one message. The server computes a running SHA-256, which it will send
   every BATCH_SIZE octets back to us. When we receive a response, we
   repeat by sending another batch of data.
   """

   def sendOneBatch(self):
      data = randomByteString(BATCH_SIZE)

      # Note, that this could complete the frame, when the frame length is
      # reached. Since the frame length here is 2^63, we don't bother, since
      # it'll take _very_ long to reach that.
      self.sendMessageFrameData(data)

   def onOpen(self):
      self.count = 0
      self.beginMessage(binary = True)
      # 2^63 - This is the maximum imposed by the WS protocol
      self.beginMessageFrame(0x7FFFFFFFFFFFFFFF)
      self.sendOneBatch()

   def onMessage(self, message, binary):
      print "Digest for batch %d computed by server: %s" \
            % (self.count, message)
      self.count += 1
      self.sendOneBatch()


if __name__ == '__main__':

   factory = WebSocketClientFactory("ws://localhost:9000")
   factory.protocol = StreamingHashClientProtocol
   connectWS(factory)
   reactor.run()
