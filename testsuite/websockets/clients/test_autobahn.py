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
from optparse import OptionParser
from twisted.python import log
from twisted.internet import reactor
import autobahn
from autobahn.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS
from autobahn.case import Cases, CaseCategories, caseClasstoId


class WebSocketTestClientProtocol(WebSocketClientProtocol):

   def onOpen(self):
      if self.factory.endCaseId is None:
         print "Getting case count .."
      elif self.factory.currentCaseId <= self.factory.endCaseId:
         print "Running test case %d/%d as user agent %s on peer %s" % (self.factory.currentCaseId, self.factory.endCaseId, self.factory.agent, self.peerstr)

   def onMessage(self, msg, binary):
      if self.factory.endCaseId is None:
         self.factory.endCaseId = int(msg)
         print "Ok, will run %d cases" % self.factory.endCaseId
      else:
         self.sendMessage(msg, binary)


class WebSocketTestClientFactory(WebSocketClientFactory):

   protocol = WebSocketTestClientProtocol

   def __init__(self, url, debug, debugCodePaths):
      WebSocketClientFactory.__init__(self, url, debug = debug, debugCodePaths = debugCodePaths)

      self.endCaseId = None
      self.currentCaseId = 0

      self.updateReports = True
      self.agent = "AutobahnClient/%s" % autobahn.version
      self.resource = "/getCaseCount"

   def clientConnectionLost(self, connector, reason):
      self.currentCaseId += 1
      if self.currentCaseId <= self.endCaseId:
         self.resource = "/runCase?case=%d&agent=%s" % (self.currentCaseId, self.agent)
         connector.connect()
      elif self.updateReports:
         self.resource = "/updateReports?agent=%s" % self.agent
         self.updateReports = False
         connector.connect()
      else:
         reactor.stop()

   def clientConnectionFailed(self, connector, reason):
      print "Connection to %s failed (%s)" % (self.url, reason.getErrorMessage())
      reactor.stop()


if __name__ == '__main__':

   log.startLogging(sys.stdout)

   parser = OptionParser()
   parser.add_option("-u", "--url", dest = "url", help = "The WebSocket URL of the fuzzing server.", default = "ws://localhost:9001")
   (options, args) = parser.parse_args()

   factory = WebSocketTestClientFactory(options.url, debug = False, debugCodePaths = False)
   factory.setProtocolOptions(failByDrop = False)
   connectWS(factory)
   reactor.run()
