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

class Case7_5_1(Case):

   DESCRIPTION = """Send a close frame with invalid UTF8 payload"""

   EXPECTATION = """Clean close with protocol error or invalid utf8 code or dropped TCP."""
   
   def init(self):
      self.suppressClose = True
   
   def onConnectionLost(self, failedByMe):
      # check if we passed the test
      for e in self.expected:
         if self.compare(self.received, self.expected[e]):
            self.behavior = e
            self.passed = True
            self.result = "Actual events match at least one expected."
            break
      # check the close status
      if self.expectedClose["failedByMe"] != self.p.closedByMe:
         self.behaviorClose = Case.FAILED
         self.resultClose = "The connection was failed by the wrong endpoint"
      elif self.expectedClose["requireClean"] and not self.p.wasClean:
         self.behaviorClose = Case.FAILED
         self.resultClose = "The spec requires the connection to be failed cleanly here"
      elif self.p.remoteCloseCode != None and self.p.remoteCloseCode != self.p.CLOSE_STATUS_CODE_PROTOCOL_ERROR and self.p.remoteCloseCode != self.p.CLOSE_STATUS_CODE_INVALID_PAYLOAD:
         self.behaviorClose = Case.FAILED
         self.resultClose = "The close code should have been 1002, 1007, or empty"
      elif not self.p.isServer and self.p.droppedByMe:
         self.behaviorClose = Case.FAILED_BY_CLIENT
         self.resultClose = "It is preferred that the server close the TCP connection"
      else:
         self.behaviorClose = Case.OK
         self.resultClose = "Connection was properly closed"
   
   def onOpen(self):
      self.payload = '\xce\xba\xe1\xbd\xb9\xcf\x83\xce\xbc\xce\xb5\xed\xa0\x80\x65\x64\x69\x74\x65\x64'
      self.expected[Case.OK] = []      
      self.expectedClose = {"failedByMe":False,"closeCode":self.p.CLOSE_STATUS_CODE_PROTOCOL_ERROR,"requireClean":False}
      self.p.sendFrame(opcode = 8,payload = self.payload)
      self.p.killAfter(1)

      
