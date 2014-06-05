###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
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

from autobahn.twisted.websocket import WebSocketServerProtocol, \
                                       WebSocketServerFactory

import json
from twisted.internet.defer import Deferred, \
                                   inlineCallbacks, \
                                   returnValue


def sleep(delay):
   d = Deferred()
   reactor.callLater(delay, d.callback, None)
   return d


class SlowSquareServerProtocol(WebSocketServerProtocol):

   @inlineCallbacks
   def slowsquare(self, x):
      if x > 5:
         raise Exception("number too large")
      else:
         yield sleep(1)
         returnValue(x * x)

   @inlineCallbacks
   def onMessage(self, payload, isBinary):
      if not isBinary:
         x = json.loads(payload.decode('utf8'))
         try:
            res = yield self.slowsquare(x)
         except Exception as e:
            self.sendClose(1000, "Exception raised: {}".format(e))
         else:
            self.sendMessage(json.dumps(res).encode('utf8'))



if __name__ == '__main__':

   import sys

   from twisted.python import log
   from twisted.internet import reactor

   log.startLogging(sys.stdout)

   factory = WebSocketServerFactory("ws://localhost:9000", debug = False)
   factory.protocol = SlowSquareServerProtocol

   reactor.listenTCP(9000, factory)
   reactor.run()
