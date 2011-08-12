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

##
## Client for TCP octet trickling tests.
##
## The goal of this test program is to see how it's possible (if at all) to
## "flush octets" out the wire with TCP, so one can test a protocol implementation
## whether it's "stream clean" .. that is agnostic to the chops in which it
## receives stuff.
##
## The problem is: TCP is fundamentally stream oriented, and one has not control
## in general how the sending side TCP stacks wraps up payload into TCP segments,
## and in which chops the receiving side makes data available to an application.
##
## We use 3 tools in this test:
##
##   TCP NoDelay Option
##   queueing & deferred writes to transport
##   trigger an iteration of the reactor loop
##
## Results: When you look at wire dumps, only the version
##
##      self.send = self.send_queued
##      self.nodelay = True
##
## seems to "work".
##
## The writes (often) will result in individual TCP segments with PSH ("Push") flag set.
## http://freesoft.org/CIE/RFC/1122/88.htm
##
## Also, this version does not use internal API reactor.doIteration().
## I think this is the nearest one can get to desired effect within Python.
## The downside is an additional buffering (see the deque) for pending "trickled"
## writes.


from collections import deque
from twisted.internet import reactor, protocol


class TricklingClientProtocol(protocol.Protocol):

   def __init__(self):

      ## Test Configuration
      ## START
      ##
      #self.send = self.send_synched
      self.send = self.send_queued
      self.nodelay = True
      ##
      ## END

      self.send_queue = deque()
      self.triggered = False

   def _trigger(self):
      if not self.triggered:
         self.triggered = True
         self._send()

   def _send(self):
      if len(self.send_queue) > 0:
         e = self.send_queue.popleft()
         self.transport.write(e)
         reactor.callLater(0.000001, self._send)
      else:
         self.triggered = False

   def send_queued(self, data, sync = False, chopsize = None):
      if chopsize > 0:
         i = 0
         n = len(data)
         done = False
         while not done:
            j = i + chopsize
            if j >= n:
               done = True
               j = n
            self.send_queue.append(data[i:j])
            i += chopsize
         self._trigger()
         #print "chopped send"
      else:
         if sync or len(self.send_queue) > 0:
            self.send_queue.append(data)
            self._trigger()
            #print "synced send"
         else:
            self.transport.write(data)
            #print "normal send"

   def syncSocket(self):
      try:
         reactor.doIteration(0)
         return True
      except:
         return False # socket has already gone away ..

   def send_synched(self, data, sync = False, chopsize = None):
      if chopsize > 0:
         i = 0
         n = len(data)
         done = False
         while not done:
            j = i + chopsize
            if j >= n:
               done = True
               j = n
            self.transport.write(data[i:j])
            self.syncSocket()
            i += chopsize
      else:
         self.transport.write(data)
         if sync:
            self.syncSocket()

   def connectionMade(self):
      self.transport.setTcpNoDelay(self.nodelay)
      self.part1()

   def part1(self):
      LEN = 50
      self.send("123" * LEN)
      for i in xrange(0, LEN):
         self.send("456", sync = True)
      self.send("789" * LEN, chopsize = 1)
      self.send("123" * LEN)
      reactor.callLater(0.3, self.part2)

   def part2(self):
      self.send("xyz" * 5)
      self.send("abc" * 5, chopsize = 1)
      reactor.callLater(5, self.transport.loseConnection)


class TricklingClientFactory(protocol.ClientFactory):

   protocol = TricklingClientProtocol

   def clientConnectionFailed(self, connector, reason):
      reactor.stop()

   def clientConnectionLost(self, connector, reason):
      reactor.stop()


if __name__ == '__main__':
   factory = TricklingClientFactory()
   reactor.connectTCP("192.168.1.134", 9000, factory)
   reactor.run()
