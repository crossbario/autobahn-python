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


class NonStreamingHashServerProtocol(WebSocketServerProtocol):
   """
   Message-based WebSockets server that computes a SHA-256 for message
   payload of messages it receives. It sends back the computed digest.
   """

   def onMessage(self, msg, binary):
      ## upon receiving a message, we compute the SHA-256 digest ..
      sha256 = hashlib.sha256()
      sha256.update(msg)
      digest = sha256.hexdigest()

      ## .. and send that back to the client
      self.sendMessage(digest)
      print "Sent digest for message : %s" % digest


if __name__ == '__main__':

   factory = WebSocketServerFactory()
   factory.protocol = NonStreamingHashServerProtocol
   reactor.listenTCP(9000, factory)
   reactor.run()
