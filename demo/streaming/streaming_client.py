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

import hashlib, random, struct, binascii, gc
from twisted.internet import reactor
from autobahn.websocket import WebSocketProtocol, WebSocketClientFactory, WebSocketClientProtocol


class StreamingClientProtocol(WebSocketClientProtocol):
   """
   Streaming WebSockets client that sends random bits, all sent in 1 WebSockets
   message within frames of length 2^63.
   It can run forever in constant memory (more precisely, with a finite upper
   bound, and no bugs in GC).
   """

   ## We send data within the 1 message in frames of this size
   ##
   FRAME_SIZE = 0x7FFFFFFFFFFFFFFF # 2^63 - This is the maximum imposed by the WS protocol

   ## We send data within frames in chunks of BUFFER_SIZE bytes
   ##
   SEND_SIZE = 64 * 2**10

   ## We want updates of the running digest every BATCH_SIZE bytes
   ##
   BATCH_SIZE = 1 * 2**20


   def onOpen(self):
      ## batch counter for batches send by client
      self.count = 0

      ## batch counter for batch digests received by server
      self.scount = 0

      ## we'll compute the digest also ourselfes, since this
      ## is a demo, and we want to verify everything works
      self.sha256 = hashlib.sha256()

      ## we start a binary message
      self.beginMessage(opcode = WebSocketProtocol.MESSAGE_TYPE_BINARY)

      ## we start a new frame within the message
      ##
      self.beginMessageFrame(StreamingClientProtocol.FRAME_SIZE)

      ## then we send 4 batches out .. this is to get the server going
      ##
      for i in xrange(0, 3):
         self.sendBatch()


   def sendBatch(self):
      ## compute random bits for batch and send data on the fly
      ##
      i = 0
      while i < StreamingClientProtocol.BATCH_SIZE:
         data = self.randomByteString(StreamingClientProtocol.SEND_SIZE)
         self.sha256.update(data)

         ## now send the data streaming within the frame ..
         ##
         if self.sendMessageFrameData(data) <= 0:
            ## Note, this will only be reached when frame size was reached.
            ## In that case, we just start another fragment in the message.
            ## When max. frame size 2^63 is chosen, we practically will never
            ## come here!
            self.beginMessageFrame(StreamingClientProtocol.FRAME_SIZE)
            print "new frame started!"
         i += StreamingClientProtocol.SEND_SIZE

      ## we compute the digest also ourselfes for checking
      digest = self.sha256.hexdigest()
      print "Digest up to batch %d computed by me: %s.." % (self.count, digest[:8])
      self.count += 1


   def onMessage(self, msg, binary):
      print "Digest up to batch %d computed by server: %s.." % (self.scount, msg[:8])
      self.scount += 1

      ## upon receiving computed digest from server, we queue up
      ## another chunk .. essentially, this is our flow control - otherwise
      ## we would enqueue chunks in the Twisted/TCP/IP stack as fast as we could
      ## and consume more and more memory.
      self.sendBatch()

   def randomByteString(self, len):
      return ''.join([struct.pack("!Q", random.getrandbits(64)) for x in xrange(0, len / 8 + int(len % 8 > 0))])[:len]


class StreamingClientFactory(WebSocketClientFactory):

   protocol = StreamingClientProtocol

   def __init__(self, debug = False):
      self.path = "/"
      self.debug = debug


if __name__ == '__main__':

   factory = StreamingClientFactory()
   reactor.connectTCP("localhost", 9000, factory)
   reactor.run()
