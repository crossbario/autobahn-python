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

TESTCMD = """message_test:uri=%(uri)s;token=%(token)s;size=%(size)d;count=%(count)d;timeout=10000;binary=true;sync=true;correctness=exact;"""

SERVERS = [{'name': 'Autobahn/0.4.11', 'uri': 'ws://192.168.1.120:9000/'},
           {'name': 'WebSocket++/HEAD', 'uri': 'ws://192.168.1.133:9002/'}]

SIZES = [[10000, 0],
         [10000, 16],
         [10000, 64],
         [10000, 256],
         [10000, 1024],
         [10000, 4096],
         ]

#SIZES = [[10000, 0]]

class WsPerfCommanderProtocol(WebSocketClientProtocol):

   def sendNext(self):
      if self.current == len(self.tests):
         return True
      test = self.tests[self.current]
      cmd = TESTCMD % test
      if self.factory.debugWsPerf:
         print cmd
      print "Starting test for testee %s" % test['name']
      self.sendMessage(cmd)
      self.current += 1

   def setupTests(self):
      for server in SERVERS:
         for size in SIZES:
            id = newid()
            test = {'uri': server['uri'],
                    'name': server['name'],
                    'count': size[0],
                    'size': size[1],
                    'token': id}
            self.tests.append(test)
            self.testdefs[id] = test

   def onTestsComplete(self):
      print "ALL TESTS COMPLETE!"
      if factory.debugWsPerf:
         self.pp.pprint(self.testresults)
      for test in self.tests:
         result = self.testresults[test['token']]
         median_microsecs = int(round(result['data']['median'] / 1000))
         print ','.join([str(x) for x in [test['name'], test['size'], median_microsecs]])
      reactor.stop()

   def onOpen(self):
      self.pp = pprint.PrettyPrinter(indent = 3)
      self.tests = []
      self.testdefs = {}
      self.testresults = {}
      self.current = 0
      self.setupTests()
      self.sendNext()

   def onMessage(self, msg, binary):
      if not binary:
         try:
            o = json.loads(msg)
            if o['type'] == u'test_complete':
               if self.sendNext():
                  self.onTestsComplete()
            elif o['type'] == u'test_data':
               if self.factory.debugWsPerf:
                  self.pp.pprint(o)
               self.testresults[o['token']] = o
         except ValueError, e:
            pass


if __name__ == '__main__':

   #log.startLogging(sys.stdout)
   factory = WebSocketClientFactory("ws://192.168.1.141:9002", debug = False)
   factory.debugWsPerf = False
   factory.protocol = WsPerfCommanderProtocol
   connectWS(factory)
   reactor.run()
