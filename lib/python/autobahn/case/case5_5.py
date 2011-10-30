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

class Case5_5(Case):

   DESCRIPTION = """Send text Message fragmented into 2 fragments, octets are sent in octet-wise chops."""

   EXPECTATION = """Message is processed and echo'ed back to us."""

   def onOpen(self):
      fragments = ["fragment1", "fragment2"]
      self.expected[Case.OK] = [("message", ''.join(fragments), False)]
      self.expectedClose = {"closedByMe":True,"closeCode":[self.p.CLOSE_STATUS_CODE_NORMAL],"requireClean":True}
      self.p.sendFrame(opcode = 1, fin = False, payload = fragments[0], chopsize = 1)
      self.p.sendFrame(opcode = 0, fin = True, payload = fragments[1], chopsize = 1)
      self.p.closeAfter(1)
