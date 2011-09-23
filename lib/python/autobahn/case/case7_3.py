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

class Case7_3_1(Case):

   DESCRIPTION = """Send invalid close frame"""

   EXPECTATION = """Receive echo'ed text message. Clean close with normal code."""
   
   def init(self):
      self.plen = 0;
      self.payload = ""
   
   def onOpen(self):
      payload = "Hello World!"
      
      
      plen = 0
      payload = ""

      if code is not None:

         if (not (code >= 3000 and code <= 3999)) and \
            (not (code >= 4000 and code <= 4999)) and \
            code not in WebSocketProtocol.CLOSE_STATUS_CODES_ALLOWED:
            raise Exception("invalid status code %d for close frame" % code)

         payload = struct.pack("!H", code)
         plen = 2

         if reason is not None:
            reason = reason.encode("UTF-8")
            plen += len(reason)
         else:
            reason = ""

         if plen > 125:
            raise Exception("close frame payload larger than 125 octets")

         payload += reason

      else:
         if reason is not None and reason != "":
            raise Exception("status reason '%s' without status code in close frame" % reason)
      self.sendFrame(opcode = 8, payload = payload)
      
      
      self.expected[Case.OK] = [("message", payload, False)]      
      self.expectedClose = {"failedByMe":False,"closeCode":self.p.CLOSE_STATUS_CODE_NORMAL,"requireClean":True}
      self.p.sendFrame(opcode = 1, payload = payload)
      self.p.sendClose(self.p.CLOSE_STATUS_CODE_NORMAL);
      self.p.sendFrame(opcode = 9)
      self.p.killAfter(1)

      
