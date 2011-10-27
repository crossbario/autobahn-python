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

class Case5_18(Case):

   DESCRIPTION = """Send text Message fragmented into 2 fragments, with both frame opcodes set to text, sent in one chop."""

   EXPECTATION = """The connection is failed immediately, since all data frames after the initial data frame must have opcode 0."""

   def onOpen(self):
      self.expected[Case.OK] = []
      self.expectedClose = {"closedByMe":False,"closeCode":[self.p.CLOSE_STATUS_CODE_PROTOCOL_ERROR],"requireClean":False}
      self.p.sendFrame(opcode = 1, fin = False, payload = "fragment1")
      self.p.sendFrame(opcode = 1, fin = True, payload = "fragment2")
      self.p.killAfter(1)
