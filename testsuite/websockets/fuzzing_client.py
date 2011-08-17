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
from autobahn.fuzzing import FuzzingClientProtocol, FuzzingClientFactory
from autobahn.case import Cases, CasesIndices, CaseCategories, caseClasstoId, caseIdtoIdTuple, caseIdTupletoId
import datetime
import json
import re


def getUtcNow():
   now = datetime.datetime.utcnow()
   return now.strftime("%Y-%m-%dT%H:%M:%SZ")


class FuzzingClientDriverProtocol(FuzzingClientProtocol):

   def connectionMade(self):
      FuzzingClientProtocol.connectionMade(self)
      self.caseAgent = self.factory.agent
      self.case = self.factory.currentCaseIndex
      self.Case = Cases[self.case - 1]
      self.runCase = self.Case(self)
      self.caseStarted = getUtcNow()
      print "Running test case ID %s for agent %s from peer %s" % (caseClasstoId(self.Case), self.caseAgent, self.peerstr)


class FuzzingClientDriverFactory(FuzzingClientFactory):

   protocol = FuzzingClientDriverProtocol

   def __init__(self, spec, debug = False):
      FuzzingClientFactory.__init__(self, debug)
      self.spec = spec
      self.specCases = []
      for c in self.spec["cases"]:
         if c.find('*') >= 0:
            s = c.replace('.', '\.').replace('*', '.*')
            p = re.compile(s)
            t = []
            for x in CasesIndices.keys():
               if p.match(x):
                  t.append(caseIdtoIdTuple(x))
            for h in sorted(t):
               self.specCases.append(caseIdTupletoId(h))
         else:
            self.specCases.append(c)
      print "Ok, will run %d test cases against %d servers" % (len(self.specCases), len(spec["servers"]))
      self.currServer = -1
      if self.nextServer():
         if self.nextCase():
            reactor.connectTCP(self.hostname, self.port, self)


   def nextServer(self):
      self.currSpecCase = -1
      self.currServer += 1
      if self.currServer < len(spec["servers"]):
         s = spec["servers"][self.currServer]
         self.agent = s["agent"]
         self.hostname = s["hostname"]
         self.port = s["port"]
         return True
      else:
         return False


   def nextCase(self):
      self.currSpecCase += 1
      if self.currSpecCase < len(self.specCases):
         self.currentCaseId = self.specCases[self.currSpecCase]
         self.currentCaseIndex = CasesIndices[self.currentCaseId]
         return True
      else:
         return False


   def clientConnectionLost(self, connector, reason):
      if self.nextCase():
         connector.connect()
      else:
         if self.nextServer():
            if self.nextCase():
               reactor.connectTCP(self.hostname, self.port, self)
         else:
            self.createReports()
            reactor.stop()



if __name__ == '__main__':

   log.startLogging(sys.stdout)
   spec = json.loads(open("fuzzing_client_spec.json").read())
   factory = FuzzingClientDriverFactory(spec = spec)
   reactor.run()
