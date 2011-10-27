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
from autobahn.websocket import WebSocketProtocol


class Case6_4_4(Case6_3_1):

   DESCRIPTION = """Send invalid UTF-8 text message in one frame, but 3 chops. First chop is valid, then wait, then send 2nd chop with payload octet making the sequence invalid, then wait, then send test rest of payload in last chop.<br><br>MESSAGE:<br>%s<br>%s""" % (Case6_3_1.PAYLOAD, binascii.b2a_hex(Case6_3_1.PAYLOAD))

   EXPECTATION = """The first chop is accepted, we expect to timeout on the first wait. The 2nd chop should be rejected immediately (fail fast on UTF-8) upon receiving the offending octet. If we timeout, we expect the connection is failed at least then, since the payload is not valid UTF-8."""

   def onOpen(self):

      self.expected[Case.OK] = [("timeout", "A")]
      self.expected[Case.NON_STRICT] = [("timeout", "A"), ("timeout", "B")]

      self.expectedClose = {"failedByMe":False,"closeCode":[self.p.CLOSE_STATUS_CODE_INVALID_PAYLOAD],"requireClean":False}

      self.p.beginMessage(opcode = WebSocketProtocol.MESSAGE_TYPE_TEXT)
      self.p.beginMessageFrame(len(self.PAYLOAD))
      self.p.sendMessageFrameData(self.PAYLOAD[:12])
      self.p.continueLater(1, self.part2, "A")

   def part2(self):
      self.received.append(("timeout", "A"))
      self.p.sendMessageFrameData(self.PAYLOAD[12])
      self.p.continueLater(1, self.part3, "B")

   def part3(self):
      self.received.append(("timeout", "B"))
      self.p.sendMessageFrameData(self.PAYLOAD[13:])
      self.p.endMessage()

      self.p.killAfter(1)
