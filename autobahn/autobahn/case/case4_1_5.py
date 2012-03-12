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

class Case4_1_5(Case):

   DESCRIPTION = """Send small text message, then send frame with reserved non-control <b>Opcode = 7</b> and non-empty payload, then send Ping."""

   EXPECTATION = """Echo for first message is received, but then connection is failed immediately, since reserved opcode frame is used. A Pong is not received."""

   def onOpen(self):
      payload = "Hello, world!"
      self.expected[Case.OK] = [("message", payload, False)]
      self.expected[Case.NON_STRICT] = []
      self.expectedClose = {"closedByMe":False,"closeCode":[self.p.CLOSE_STATUS_CODE_PROTOCOL_ERROR],"requireClean":False}
      self.p.sendFrame(opcode = 1, payload = payload, chopsize = 1)
      self.p.sendFrame(opcode = 7, payload = payload, chopsize = 1)
      self.p.sendFrame(opcode = 9, chopsize = 1)
      self.p.killAfter(1)
