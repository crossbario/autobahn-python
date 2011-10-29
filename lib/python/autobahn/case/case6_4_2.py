# coding=utf-8

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

import binascii
from case import Case
from case6_4_1 import Case6_4_1
from autobahn.websocket import WebSocketProtocol


class Case6_4_2(Case6_4_1):

   DESCRIPTION = """Same as Case 6.4.1, but in 2nd frame, we send only up to and including the octet making the complete payload invalid.
<br><br>MESSAGE PARTS:<br>
PART1 = %s (%s)<br>
PART2 = %s (%s)<br>
PART3 = %s (%s)<br>
""" % (Case6_4_1.PAYLOAD[:12], binascii.b2a_hex(Case6_4_1.PAYLOAD[:12]), Case6_4_1.PAYLOAD[12], binascii.b2a_hex(Case6_4_1.PAYLOAD[12]), Case6_4_1.PAYLOAD[13:], binascii.b2a_hex(Case6_4_1.PAYLOAD[13:]))

   EXPECTATION = """The first frame is accepted, we expect to timeout on the first wait. The 2nd frame should be rejected immediately (fail fast on UTF-8). If we timeout, we expect the connection is failed at least then, since the complete message payload is not valid UTF-8."""

   def onOpen(self):

      self.expected[Case.OK] = [("timeout", "A")]
      self.expected[Case.NON_STRICT] = [("timeout", "A"), ("timeout", "B")]

      self.expectedClose = {"closedByMe": False, "closeCode": [self.p.CLOSE_STATUS_CODE_INVALID_PAYLOAD], "requireClean": False}

      self.p.sendFrame(opcode = 1, fin = False, payload = self.PAYLOAD[:12])
      self.p.continueLater(1, self.part2, "A")

   def part2(self):
      if self.p.state == WebSocketProtocol.STATE_OPEN:
         self.received.append(("timeout", "A"))
         self.p.sendFrame(opcode = 0, fin = False, payload = self.PAYLOAD[12])
         self.p.continueLater(1, self.part3, "B")

   def part3(self):
      if self.p.state == WebSocketProtocol.STATE_OPEN:
         self.received.append(("timeout", "B"))
         self.p.sendFrame(opcode = 0, fin = True, payload = self.PAYLOAD[13:])
         self.p.killAfter(1)
