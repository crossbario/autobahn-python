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

import sys
from twisted.internet import reactor
from twisted.python import log
from autobahn.websocket import WebSocketService, WebSocketServiceConnection

class EchoServiceConnection(WebSocketServiceConnection):

   def onMessage(self, msg, binary):
      self.sendMessage(msg, binary)


class EchoService(WebSocketService):

   protocol = EchoServiceConnection

   def __init__(self, debug):
      self.debug = debug


def main():
   log.startLogging(sys.stdout)
   service = EchoService(debug = True)
   reactor.listenTCP(9000, service)
   reactor.run()

if __name__ == '__main__':
   main()
