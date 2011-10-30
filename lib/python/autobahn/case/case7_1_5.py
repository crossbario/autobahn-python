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

class Case7_1_5(Case):

   DESCRIPTION = """Send message fragment1 followed by close then fragment"""

   EXPECTATION = """Clean close with normal code."""
   
   def init(self):
      self.suppressClose = True
   
   def onOpen(self):
      fragments = ["fragment1", "fragment2"]
      self.expected[Case.OK] = []      
      self.expectedClose = {"closedByMe":True,"closeCode":[self.p.CLOSE_STATUS_CODE_NORMAL],"requireClean":True}
      self.p.sendFrame(opcode = 1, fin = False, payload = fragments[0])
      self.p.sendClose(self.p.CLOSE_STATUS_CODE_NORMAL)
      self.p.sendFrame(opcode = 0, fin = True, payload = fragments[1])
      self.p.killAfter(1)

      
