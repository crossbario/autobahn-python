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

class Case1_2_8(Case):

   DESCRIPTION = """Send binary message message with payload of length 65536. Sent out data in chops of 997 octets."""

   EXPECTATION = """Receive echo'ed binary message (with payload as sent). Clean close with normal code."""

   def onOpen(self):
      payload = "\xfe" * 65536
      self.expected[Case.OK] = [("message", payload, True)]
      self.expectedClose = {"closedByMe":True,"closeCode":[self.p.CLOSE_STATUS_CODE_NORMAL],"requireClean":True}
      self.p.sendFrame(opcode = 2, payload = payload, chopsize = 997)
      self.p.killAfter(10)
