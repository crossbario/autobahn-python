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

class Case7_1_6(Case):

   DESCRIPTION = """Send 256K message followed by close then a ping"""

   EXPECTATION = """Case outcome depends on implimentation defined close behavior. Message and close frame are sent back to back. If the close frame is processed before the text message write is complete (as can happen in asyncronous processing models) the close frame is processed first and the text message may not be recieved or may only be partially recieved."""
   
   def init(self):
      self.suppressClose = True
      self.DATALEN = 256 * 2**10
      self.PAYLOAD = "BAsd7&jh23"

   def onConnectionLost(self, failedByMe):
      Case.onConnectionLost(self, failedByMe)
      
      self.passed = True
      
      
      if self.behavior == Case.OK:
         self.result = "Text message was processed before close."
      elif self.behavior == Case.NON_STRICT:
         self.result = "Close was processed before text message could be returned."
      
      self.behavior = Case.INFORMATIONAL
      self.behaviorClose = Case.INFORMATIONAL
      
   def onOpen(self):
      payload = "Hello World!"
      self.expected[Case.OK] = [("message", payload, False)] 
      self.expected[Case.NON_STRICT] = []      
      self.expectedClose = {"closedByMe":True,"closeCode":[self.p.CLOSE_STATUS_CODE_NORMAL],"requireClean":True}
      self.p.sendFrame(opcode = 1, payload = self.PAYLOAD, payload_len = self.DATALEN)
      self.p.sendFrame(opcode = 1, payload = payload)
      self.p.sendClose(self.p.CLOSE_STATUS_CODE_NORMAL)
      self.p.sendFrame(opcode = 9)
      self.p.killAfter(1)

      
