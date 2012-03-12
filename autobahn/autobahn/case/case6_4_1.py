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
from autobahn.websocket import WebSocketProtocol


class Case6_4_1(Case):

   PAYLOAD1 = '\xce\xba\xe1\xbd\xb9\xcf\x83\xce\xbc\xce\xb5'
   #PAYLOAD2 = '\xed\xa0\x80' # invalid exactly on byte 12 (\xa0)
   PAYLOAD2 = '\xf4\x90\x80\x80' #invalid exactly on byte 12 (\x90)
   PAYLOAD3 = '\x65\x64\x69\x74\x65\x64'
   PAYLOAD = PAYLOAD1 + PAYLOAD2 + PAYLOAD3

   DESCRIPTION = """Send invalid UTF-8 text message in 3 fragments (frames).
First frame payload is valid, then wait, then 2nd frame which contains the payload making the sequence invalid, then wait, then 3rd frame with rest.
Note that PART1 and PART3 are valid UTF-8 in themselves, PART2 is a 0x11000 encoded as in the UTF-8 integer encoding scheme, but the codepoint is invalid (out of range).
<br><br>MESSAGE PARTS:<br>
PART1 = %s (%s)<br>
PART2 = %s (%s)<br>
PART3 = %s (%s)<br>
""" % (PAYLOAD1, binascii.b2a_hex(PAYLOAD1), PAYLOAD2, binascii.b2a_hex(PAYLOAD2), PAYLOAD3, binascii.b2a_hex(PAYLOAD3))

   EXPECTATION = """The first frame is accepted, we expect to timeout on the first wait. The 2nd frame should be rejected immediately (fail fast on UTF-8). If we timeout, we expect the connection is failed at least then, since the complete message payload is not valid UTF-8."""

   def onOpen(self):

      self.expected[Case.OK] = [("timeout", "A")]
      self.expected[Case.NON_STRICT] = [("timeout", "A"), ("timeout", "B")]

      self.expectedClose = {"closedByMe": False, "closeCode": [self.p.CLOSE_STATUS_CODE_INVALID_PAYLOAD], "requireClean": False}

      self.p.sendFrame(opcode = 1, fin = False, payload = self.PAYLOAD1)
      self.p.continueLater(1, self.part2, "A")

   def part2(self):
      if self.p.state == WebSocketProtocol.STATE_OPEN:
         self.received.append(("timeout", "A"))
         self.p.sendFrame(opcode = 0, fin = False, payload = self.PAYLOAD2)
         self.p.continueLater(1, self.part3, "B")

   def part3(self):
      if self.p.state == WebSocketProtocol.STATE_OPEN:
         self.received.append(("timeout", "B"))
         self.p.sendFrame(opcode = 0, fin = True, payload = self.PAYLOAD3)
         self.p.killAfter(1)
