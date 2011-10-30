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
import binascii

class Case6_2_2(Case):

   PAYLOAD1 = "Hello-µ@ßöä"
   PAYLOAD2 = "üàá-UTF-8!!"

   DESCRIPTION = """Send a valid UTF-8 text message in two fragments, fragmented on UTF-8 code point boundary.<br><br>MESSAGE FRAGMENT 1:<br>%s<br>%s<br><br>MESSAGE FRAGMENT 2:<br>%s<br>%s""" % (PAYLOAD1, binascii.b2a_hex(PAYLOAD1), PAYLOAD2, binascii.b2a_hex(PAYLOAD2))

   EXPECTATION = """The message is echo'ed back to us."""

   def onOpen(self):

      self.expected[Case.OK] = [("message", self.PAYLOAD1 + self.PAYLOAD2, False)]
      self.expectedClose = {"closedByMe":True,"closeCode":[self.p.CLOSE_STATUS_CODE_NORMAL],"requireClean":True}
      self.p.sendFrame(opcode = 1, fin = False, payload = self.PAYLOAD1)
      self.p.sendFrame(opcode = 0, fin = True, payload = self.PAYLOAD2)
      self.p.closeAfter(1)
