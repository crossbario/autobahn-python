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

import random, struct
from zope.interface import implements
from twisted.internet import reactor, interfaces
from autobahn.websocket import WebSocketProtocol, WebSocketClientFactory, WebSocketClientProtocol


FRAME_SIZE = 0x7FFFFFFFFFFFFFFF # 2^63 - This is the maximum imposed by the WS protocol
#FRAME_SIZE = 64 * 2**10 # 64k
#FRAME_SIZE = 1 * 2**20 # 1M


class RandomByteStreamProducer:
   """
   A Twisted Push Producer generating a stream of random octets.
   """
   implements(interfaces.IPushProducer)


   def randomByteString(self, len):
      """
      Generate a string of random bytes.
      """
      return ''.join([struct.pack("!Q", random.getrandbits(64)) for x in xrange(0, len / 8 + int(len % 8 > 0))])[:len]

   def __init__(self, proto):
      self.proto = proto
      self.started = False
      self.paused = False

   def pauseProducing(self):
      """
      Called when we are asked to pause producing/sending, because the
      receiver is busy consuming our stuff.
      """
      self.paused = True

   def resumeProducing(self):
      """
      Called when we are asked to resume producing/sending, because the
      receiver has consumed and can take more.
      """
      self.paused = False

      if not self.started:
         ## upon starting, we create a new WebSockets binary message and
         ## begin a new frame ..
         self.proto.beginMessage(opcode = WebSocketProtocol.MESSAGE_TYPE_BINARY)
         self.proto.beginMessageFrame(FRAME_SIZE)
         self.started = True

      while not self.paused:
         ## while running, we generate random bits ..
         data = self.randomByteString(1024)

         ## .. send them as frame payload
         if self.proto.sendMessageFrameData(data) <= 0:

            ## when the frame is finished, we get here, and
            ## we just start a new frame.
            self.proto.beginMessageFrame(FRAME_SIZE)
            print "new frame started!"

   def stopProducing(self):
        pass


class StreamingHashClientProtocol(WebSocketClientProtocol):
   """
   Streaming WebSockets client that generates stream of random octets
   sent to streaming WebSockets server, which computes a running SHA-256,
   which it will send every BATCH_SIZE octets back to us.

   This client can run forever in constant memory (more precisely, with a
   finite upper bound, and with no bugs in GC).
   """

   def onOpen(self):
      self.scount = 0

      ## when WebSockets handshake is complete, we create our producer,
      ## register and resume it
      ##
      producer = RandomByteStreamProducer(self)
      self.registerProducer(producer, True)
      producer.resumeProducing()

   def onMessage(self, msg, binary):
      print "Digest for batch %d computed by server: %s.." % (self.scount, msg[:8])
      self.scount += 1


if __name__ == '__main__':

   factory = WebSocketClientFactory()
   factory.protocol = StreamingHashClientProtocol
   reactor.connectTCP("localhost", 9000, factory)
   reactor.run()
