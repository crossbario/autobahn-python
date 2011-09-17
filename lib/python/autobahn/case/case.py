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

from autobahn.websocket import WebSocketProtocol
from twisted.python import log
import pickle
import textwrap


class Case:

   FAILED = "FAILED"
   OK = "OK"
   NON_STRICT = "NON-STRICT"

   SUBCASES = []

   def __init__(self, protocol):
      self.p = protocol
      self.received = []
      self.expected = {}
      self.behavior = Case.FAILED
      self.result = "Actual events differ from any expected."
      self.reportTime = False
      self.subcase = None
      self.init()

   def getSubcaseCount(self):
      return len(Case.SUBCASES)

   def setSubcase(self, subcase):
      self.subcase = subcase

   def init(self):
      pass

   def onOpen(self):
      pass

   def onMessage(self, msg, binary):
      self.received.append(("message", msg, binary))
      self.finishWhenDone()

   def onPing(self, payload):
      self.received.append(("ping", payload))
      self.finishWhenDone()

   def onPong(self, payload):
      self.received.append(("pong", payload))
      self.finishWhenDone()

   def onClose(self, code, reason):
      pass

   def compare(self, obj1, obj2):
      return pickle.dumps(obj1) == pickle.dumps(obj2)

   def onConnectionLost(self, failedByMe):
      self.received.append(("failedByMe", failedByMe))
      for e in self.expected:
         if self.compare(self.received, self.expected[e]):
            self.behavior = e
            self.passed = True
            self.result = "Actual events match at least one expected."
            break

   def finishWhenDone(self):
      for e in self.expected:
         # when we expect to fail the connection ourselfes and already
         # received everything before, we immediately fail the connection
         if self.expected[e][-1] == ("failedByMe", True):
            if self.compare(self.received, self.expected[e][:-1]):
               self.p.failConnection()
