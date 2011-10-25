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

class Case7_3_6(Case):

   DESCRIPTION = """Send a close frame with payload length 126"""

   EXPECTATION = """Clean close with protocol error code or dropped TCP connection."""
   
   def init(self):
      self.suppressClose = True
      
   def onOpen(self):
      self.payload = "\x03\xe8"+("*" * 125)
      self.expected[Case.OK] = []      
      self.expectedClose = {"failedByMe":True,"closeCode":[self.p.CLOSE_STATUS_CODE_PROTOCOL_ERROR],"requireClean":False}
      self.p.sendCloseFrame(self.p.CLOSE_STATUS_CODE_NORMAL, reasonUtf8 = self.payload)
      self.p.killAfter(1)

      
