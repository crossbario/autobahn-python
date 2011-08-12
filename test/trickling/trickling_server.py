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
## Server for TCP octet trickling tests.
##

from twisted.internet import reactor, protocol

class TricklingServerProtocol(protocol.Protocol):

   def __init__(self):
      pass

   def connectionMade(self):
      print "client accepted"
      self.transport.setTcpNoDelay(True)
      self.stats = {}

   def connectionLost(self, reason):
      print "client lost"
      for s in sorted(self.stats):
         print "%dx chop of length %d" % (self.stats[s], s)

   def dataReceived(self, data):
      l = len(data)
      self.stats[l] = self.stats.get(l, 0) + 1
      #print data


class TricklingServerFactory(protocol.ServerFactory):

   protocol = TricklingServerProtocol

   def __init__(self):
      pass

   def startFactory(self):
      pass

   def stopFactory(self):
      pass


if __name__ == '__main__':
   factory = TricklingServerFactory()
   reactor.listenTCP(9000, factory)
   reactor.run()
