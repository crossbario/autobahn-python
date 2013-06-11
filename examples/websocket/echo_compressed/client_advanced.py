###############################################################################
##
##  Copyright 2011-2013 Tavendo GmbH
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

from autobahn.websocket import WebSocketClientFactory, \
                               WebSocketClientProtocol, \
                               connectWS

from autobahn.compress import *



class EchoClientProtocol(WebSocketClientProtocol):

   def onConnect(self, connectionResponse):
      print "WebSocket extensions in use: %s" % connectionResponse.extensions

   def sendHello(self):
      self.sendMessage("Hello, world!" * 100)

   def onOpen(self):
      self.sendHello()

   def onMessage(self, msg, binary):
      print "Got echo: " + msg
      reactor.callLater(1, self.sendHello)


if __name__ == '__main__':

   if len(sys.argv) < 2:
      print "Need the WebSocket server address, i.e. ws://localhost:9000"
      sys.exit(1)

   if len(sys.argv) > 2 and sys.argv[2] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   factory = WebSocketClientFactory(sys.argv[1],
                                    debug = debug,
                                    debugCodePaths = debug)

   factory.protocol = EchoClientProtocol

   ## Advanced usage: specify exact list of offers ("PMCE") we announce to server.
   ##
   ## Examples:
   ##

   ## this is just what the default constructor for PerMessageDeflateOffer
   ## creates anyway
   offers1 = [PerMessageDeflateOffer(acceptNoContextTakeover = True,
                                     acceptMaxWindowBits = True,
                                     requestNoContextTakeover = False,
                                     requestMaxWindowBits = 0)]

   ## request the server to use a sliding window of 2^8 bytes
   offers2 = [PerMessageDeflateOffer(True, True, False, 8)]

   ## request the server to use a sliding window of 2^8 bytes, but let the
   ## server fall back to "standard" if server does not support the setting
   offers3 = [PerMessageDeflateOffer(True, True, False, 8),
              PerMessageDeflateOffer(True, True, False, 0)]

   ## request "no context takeover", accept the same, but deny setting
   ## a sliding window. no fallback!
   offers4 = [PerMessageDeflateOffer(True, False, True, 0)]

   ## offer "permessage-snappy", "permessage-bzip2" and "permessage-deflate"
   ## note that the first 2 are currently not even in an RFC draft
   ##
   offers5 = []
#   if PERMESSAGE_COMPRESSION_EXTENSION.has_key('permessage-snappy'):
#      ## this require snappy to be installed
#      offers5.append(PerMessageSnappyOffer())
   offers5.append(PerMessageBzip2Offer(True, 1))
   offers5.append(PerMessageDeflateOffer())

   #factory.setProtocolOptions(perMessageCompressionOffers = offers1)
   #factory.setProtocolOptions(perMessageCompressionOffers = offers2)
   #factory.setProtocolOptions(perMessageCompressionOffers = offers3)
   #factory.setProtocolOptions(perMessageCompressionOffers = offers4)
   factory.setProtocolOptions(perMessageCompressionOffers = offers5)

   #factory.setProtocolOptions(autoFragmentSize = 4)

   connectWS(factory)
   reactor.run()
