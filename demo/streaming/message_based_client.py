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

import hashlib, random, struct, binascii
from twisted.internet import reactor
from autobahn.websocket import WebSocketClientFactory, WebSocketClientProtocol

MESSAGE_SIZE = 10 * 2**20


class NonStreamingHashClientProtocol(WebSocketClientProtocol):
   """
   Message-based WebSockets client that generates stream of random octets
   sent to streaming WebSockets server in one message. The server will
   respond to us with the SHA-256 computed over message payload. When
   we receive response, we repeat.
   """

   def randomByteString(self, len):
      """
      Generate a string of random bytes.
      """
      return ''.join([struct.pack("!Q", random.getrandbits(64)) for x in xrange(0, len / 8 + int(len % 8 > 0))])[:len]

   def sendBatch(self):
      """
      Send out a WebSockets binary message with random bytes.
      """
      data = self.randomByteString(MESSAGE_SIZE)
      self.sendMessage(data, True)

   def onOpen(self):
      self.scount = 0
      ## send a first batch when WS handshake has been completed
      self.sendBatch()

   def onMessage(self, msg, binary):
      print "Digest for message %d computed by server: %s" % (self.scount, msg)
      self.scount += 1
      ## upon receiving a batch digest, send another
      self.sendBatch()


if __name__ == '__main__':

   factory = WebSocketClientFactory()
   factory.protocol = NonStreamingHashClientProtocol
   reactor.connectTCP("localhost", 9000, factory)
   reactor.run()
