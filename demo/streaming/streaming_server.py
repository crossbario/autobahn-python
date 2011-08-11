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

import sys, hashlib
from twisted.internet import reactor
from twisted.python import log
from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol
from streaming_client import StreamingClientProtocol

class StreamingServerProtocol(WebSocketServerProtocol):
   """
   Streaming WebSockets server that computes a running SHA-256 for data
   received. It will respond every BATCH_SIZE bytes with the digest
   up to that point.
   It can run forever in constant memory (more precisely, with a finite upper
   bound, and with no bugs in GC).
   """

   def sendDigest(self, final = False):
      digest = self.sha256.hexdigest()
      self.sendMessage(digest)
      if not final:
         print "Sent digest up to batch %d : %s.." % (self.count, digest[:8])
      else:
         print "Sent final digest for full message : %s" % digest


   def onMessageBegin(self, opcode):
      self.sha256 = hashlib.sha256()
      self.count = 0
      self.received = 0
      self.next = StreamingClientProtocol.BATCH_SIZE


   def onMessageFrameBegin(self, length, reserved):
      pass


   def onMessageFrameData(self, data):
      length = len(data)
      self.received += length

      ## when the data received exceeds the next BATCH_SIZE ..
      if self.received >= self.next:

         ## we compute and send digest up to that chunk ..
         rest = length - (self.received - self.next)
         self.sha256.update(str(data[:rest]))
         self.sendDigest()
         self.next += StreamingClientProtocol.BATCH_SIZE
         self.count += 1

         ## .. and update the digest for the rest
         self.sha256.update(str(data[rest:]))
      else:
         ## otherwise we just update the digest for received data
         self.sha256.update(str(data))


   def onMessageFrameEnd(self):
      pass


   def onMessageEnd(self):
      ## we send the final digest _should_ the message end ..
      ##
      self.sendDigest(True)


class StreamingServerFactory(WebSocketServerFactory):

   protocol = StreamingServerProtocol

   def __init__(self, debug = False):
      self.debug = debug


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = StreamingServerFactory()
   reactor.listenTCP(9000, factory)
   reactor.run()
