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

from case import Case

class Case2_10(Case):

   DESCRIPTION = """Send 10 Pings with payload."""

   EXPECTATION = """Pongs for our Pings with all the payloads. Note: This is not required by the Spec .. but we check for this behaviour anyway."""

   def init(self):
      self.chopsize = None

   def onOpen(self):
      self.expected[Case.OK] = []
      self.expected[Case.NO_CLOSE] = []
      for i in range(1, 10):
         payload = "payload-%d" % i
         self.expected[Case.OK].append(("pong", payload))
         self.expected[Case.NO_CLOSE].append(("pong", payload))
         self.p.sendFrame(opcode = 9, payload = payload, chopsize = self.chopsize)
      self.expected[Case.OK].append(("failedByMe", True))
      self.expected[Case.NO_CLOSE].append(("closedByMe", True, 1000))
      self.expected[Case.NO_CLOSE].append(("failedByMe", False))
      self.p.killAfter(3)

   def closeCase(self):
      self.p.sendClose(1000)