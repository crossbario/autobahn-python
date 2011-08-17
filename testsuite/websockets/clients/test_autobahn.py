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
from twisted.python import log
from twisted.internet import reactor
from autobahn.websocket import WebSocketClientFactory, WebSocketClientProtocol
from autobahn.case import Cases, CaseCategories, caseClasstoId


class WebSocketTestClientProtocol(WebSocketClientProtocol):

   def onOpen(self):
      if self.factory.currentCaseId <= self.factory.endCaseId:
         print "Running test case ID %s as user agent %s on peer %s" % (caseClasstoId(Cases[self.factory.currentCaseId - 1]), self.factory.agent, self.peerstr)

   def onMessage(self, msg, binary):
      self.sendMessage(msg, binary)


class WebSocketTestClientFactory(WebSocketClientFactory):

   protocol = WebSocketTestClientProtocol

   def __init__(self, debug):
      self.debug = debug

      self.startCaseId = 1;
      self.endCaseId = len(Cases);
      self.currentCaseId = self.startCaseId

      self.updateReports = True
      self.agent = "Autobahn/0.2"
      self.path = "/runCase?case=%d&agent=%s" % (self.currentCaseId, self.agent)

   def clientConnectionLost(self, connector, reason):
      self.currentCaseId += 1
      if self.currentCaseId <= self.endCaseId:
         self.path = "/runCase?case=%d&agent=%s" % (self.currentCaseId, self.agent)
         connector.connect()
      elif self.updateReports:
         self.path = "/updateReports?agent=%s" % self.agent
         self.updateReports = False
         connector.connect()
      else:
         reactor.stop()


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = WebSocketTestClientFactory(debug = False)
   reactor.connectTCP("localhost", 9000, factory)
   reactor.run()
