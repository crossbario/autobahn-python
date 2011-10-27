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

class Case6_2_3(Case):

   PAYLOAD = "Hello-µ@ßöäüàá-UTF-8!!"

   DESCRIPTION = """Send a valid UTF-8 text message in fragments of 1 octet, resulting in frames ending on positions which are not code point ends.<br><br>MESSAGE:<br>%s<br>%s""" % (PAYLOAD, binascii.b2a_hex(PAYLOAD))

   EXPECTATION = """The message is echo'ed back to us."""

   def onOpen(self):

      self.expected[Case.OK] = [("message", self.PAYLOAD, False)]
      self.expectedClose = {"closedByMe":True,"closeCode":[self.p.CLOSE_STATUS_CODE_NORMAL],"requireClean":True}
      self.p.sendMessage(self.PAYLOAD, binary = False, payload_frag_size = 1)
      self.p.closeAfter(1)
