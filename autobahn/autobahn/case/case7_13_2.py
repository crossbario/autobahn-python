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

class Case7_13_2(Case):

   DESCRIPTION = """Send close with close code 65536"""

   EXPECTATION = """Actual events are undefined by the spec."""
   
   def init(self):
      self.code = 65535
      self.suppressClose = True
   
   def onConnectionLost(self, failedByMe):
      Case.onConnectionLost(self, failedByMe)
      
      self.passed = True
      self.behavior = Case.INFORMATIONAL
      self.behaviorClose = Case.INFORMATIONAL
      self.result = "Actual events are undefined by the spec."
   
   def onOpen(self):
      self.payload = '\xce\xba\xe1\xbd\xb9\xcf\x83\xce\xbc\xce\xb5\xed\xa0\x80\x65\x64\x69\x74\x65\x64'
      self.expected[Case.OK] = []      
      self.expectedClose = {"closedByMe":True,"closeCode":[self.p.CLOSE_STATUS_CODE_NORMAL,self.code,self.p.CLOSE_STATUS_CODE_PROTOCOL_ERROR],"requireClean":False}
      self.p.sendCloseFrame(self.code)
      self.p.killAfter(1)

      
