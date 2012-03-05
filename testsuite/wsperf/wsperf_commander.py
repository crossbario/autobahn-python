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

import sys, json
from twisted.internet import reactor
from twisted.python import log
from autobahn.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

TESTCMD = """message_test:uri=ws://192.168.1.120:9000/;token=foo;size=4096;count=1000;timeout=10000;binary=true;sync=false;correctness=exact;"""


class WsPerfCommanderProtocol(WebSocketClientProtocol):

   def onOpen(self):
      self.sendMessage(TESTCMD)

   def onMessage(self, msg, binary):
      if not binary:
         try:
            o = json.loads(msg)
            print o
         except ValueError, e:
            pass


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = WebSocketClientFactory("ws://192.168.1.141:9002", debug = False)
   factory.protocol = WsPerfCommanderProtocol
   connectWS(factory)
   reactor.run()
