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

class Case3_3(Case):

   DESCRIPTION = """Send small text message, then send again with <b>RSV = 3</b>, then send Ping. Octets are sent in frame-wise chops. Octets are sent in octet-wise chops."""

   EXPECTATION = """Echo for first message is received, but then connection is failed immediately, since RSV must be 0, when no extension defining RSV meaning has been negoiated. The Pong is not received."""

   def onOpen(self):
      payload = "Hello, world!"
      self.expected[Case.OK] = [("message", payload, False)]
      self.expected[Case.NON_STRICT] = []
      self.expectedClose = {"closedByMe":False,"closeCode":[self.p.CLOSE_STATUS_CODE_PROTOCOL_ERROR],"requireClean":False}
      self.p.sendFrame(opcode = 1, payload = payload, sync = True)
      self.p.sendFrame(opcode = 1, payload = payload, rsv = 3, sync = True)
      self.p.sendFrame(opcode = 9, sync = True)
      self.p.killAfter(1)
