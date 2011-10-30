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

class Case3_7(Case):

   DESCRIPTION = """Send Close with <b>RSV = 7</b>."""

   EXPECTATION = """The connection is failed immediately, since RSV must be 0."""

   def onOpen(self):
      self.expected[Case.OK] = []
      self.expectedClose = {"closedByMe":False,"closeCode":[self.p.CLOSE_STATUS_CODE_PROTOCOL_ERROR],"requireClean":False}
      self.p.sendFrame(opcode = 8, rsv = 7)
      self.p.killAfter(1)
