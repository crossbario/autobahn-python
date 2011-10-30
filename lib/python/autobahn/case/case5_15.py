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

class Case5_15(Case):

   DESCRIPTION = """Send text Message fragmented into 2 fragments, then Continuation Frame with FIN = false where there is nothing to continue, then unfragmented Text Message, all sent in one chop."""

   EXPECTATION = """The connection is failed immediately, since there is no message to continue."""

   def onOpen(self):
      fragments = ["fragment1", "fragment2", "fragment3", "fragment4"]
      self.expected[Case.OK] = [("message", ''.join(fragments[:2]), False)]
      self.expected[Case.NON_STRICT] = []
      self.expectedClose = {"closedByMe":False,"closeCode":[self.p.CLOSE_STATUS_CODE_PROTOCOL_ERROR],"requireClean":False}
      self.p.sendFrame(opcode = 1, fin = False, payload = fragments[0])
      self.p.sendFrame(opcode = 0, fin = True, payload = fragments[1])
      self.p.sendFrame(opcode = 0, fin = False, payload = fragments[2])
      self.p.sendFrame(opcode = 1, fin = True, payload = fragments[3])
      self.p.killAfter(1)
