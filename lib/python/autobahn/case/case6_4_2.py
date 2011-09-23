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

from case import Case
from case6_3_1 import Case6_3_1
import binascii

class Case6_4_2(Case6_3_1):

   DESCRIPTION = """Send invalid UTF-8 text message in 3 fragments plus more. First is valid, then wait, then 2nd which contains the octet making the sequence invalid, then wait, then 3rd with rest. Then we send 16 frames each 64k.<br><br>MESSAGE:<br>%s<br>%s""" % (Case6_3_1.PAYLOAD, binascii.b2a_hex(Case6_3_1.PAYLOAD))

   EXPECTATION = """The first frame is accepted, we expect to timeout on the first wait. The 2nd frame should be rejected immediately (fail fast on UTF-8). If we timeout, we expect the connection is failed at least then, since the payload is not valid UTF-8."""

   def onOpen(self):

      self.expected[Case.OK] = [("timeout", "A")]
      self.expected[Case.NON_STRICT] = [("timeout", "A"), ("timeout", "B")]

      self.expectedClose = {"failedByMe":False,"closeCode":self.p.CLOSE_STATUS_CODE_INVALID_PAYLOAD,"requireClean":False}

      self.p.sendFrame(opcode = 1, fin = False, payload = self.PAYLOAD[:12])
      self.p.continueLater(1, self.part2, "A")

   def part2(self):
      self.received.append(("timeout", "A"))
      self.p.sendFrame(opcode = 0, fin = False, payload = self.PAYLOAD[12])
      self.p.continueLater(1, self.part3, "B")

   def part3(self):
      self.received.append(("timeout", "B"))
      self.p.sendFrame(opcode = 0, fin = False, payload = self.PAYLOAD[13:])
      for i in xrange(0, 16):
         self.p.sendFrame(opcode = 0, fin = False, payload = "*", payload_len = 2**16)
      self.p.sendFrame(opcode = 0, fin = True, payload = "")

      self.p.killAfter(10)
