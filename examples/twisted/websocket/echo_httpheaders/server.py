###############################################################################
##
##  Copyright (C) 2013 Tavendo GmbH
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

from autobahn.twisted.websocket import WebSocketServerFactory, \
                                       WebSocketServerProtocol, \
                                       listenWS


class EchoServerProtocol(WebSocketServerProtocol):

   def onConnect(self, request):
      headers = {'MyCustomDynamicServerHeader1': 'Hello'}

      ## Note: HTTP header field names are case-insensitive,
      ## hence AutobahnPython will normalize header field names to
      ## lower case.
      ##
      if request.headers.has_key('mycustomclientheader'):
         headers['MyCustomDynamicServerHeader2'] = request.headers['mycustomclientheader']

      ## return a pair with WS protocol spoken (or None for any) and
      ## custom headers to send in initial WS opening handshake HTTP response
      ##
      return (None, headers)

   def onMessage(self, msg, binary):
      self.sendMessage(msg, binary)



if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   headers = {'MyCustomServerHeader': 'Foobar'}

   factory = WebSocketServerFactory("ws://localhost:9000",
                                    headers = headers,
                                    debug = debug,
                                    debugCodePaths = debug)

   factory.protocol = EchoServerProtocol
   listenWS(factory)

   reactor.run()
