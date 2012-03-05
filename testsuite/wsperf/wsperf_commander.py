###############################################################################
##
##  Copyright 2012 Tavendo GmbH
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

import sys, json, pprint
from twisted.internet import reactor
from twisted.python import log
from autobahn.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS
from autobahn.util import newid

TESTCMD = """message_test:uri=ws://192.168.1.120:9000/;token=%(token)s;size=%(size)d;count=10000;timeout=10000;binary=true;sync=true;correctness=exact;"""

SERVERS = [{'name': 'Autobahn/0.4.11', 'uri': 'ws://192.168.1.120:9000'},
           {'name': 'WebSocket++/HEAD', 'uri': 'ws://192.168.1.141:9002'}]

SIZES = [0, 16, 64, 256, 1024, 4096]
#SIZES = [0]

class WsPerfCommanderProtocol(WebSocketClientProtocol):

   def sendNext(self):
      id = newid()
      cmd = TESTCMD % {'size': SIZES[self.current],
                       'token': id}
      print cmd
      self.sendMessage(cmd)
      self.current += 1

   def onOpen(self):
      self.pp = pprint.PrettyPrinter(indent = 3)
      self.current = 0
      self.sendNext()

   def onMessage(self, msg, binary):
      if not binary:
         try:
            o = json.loads(msg)
            if o['type'] == u'test_complete':
               if self.current < len(SIZES) - 1:
                  self.sendNext()
               else:
                  print "ALL TESTS COMPLETE!"
                  reactor.stop()
            elif o['type'] == u'test_data':
               self.pp.pprint(o)
         except ValueError, e:
            pass


if __name__ == '__main__':

   #log.startLogging(sys.stdout)
   factory = WebSocketClientFactory("ws://192.168.1.141:9002", debug = False)
   factory.protocol = WsPerfCommanderProtocol
   connectWS(factory)
   reactor.run()
