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

class Case6_3_1(Case):

   # invalid exactly on byte 12 (\xa0)
   PAYLOAD1 = '\xce\xba\xe1\xbd\xb9\xcf\x83\xce\xbc\xce\xb5'
   PAYLOAD2 = '\xed\xa0\x80'
   PAYLOAD3 = '\x65\x64\x69\x74\x65\x64'
   PAYLOAD = PAYLOAD1 + PAYLOAD2 + PAYLOAD3

   DESCRIPTION = """Send invalid UTF-8 text message unfragmented.<br><br>MESSAGE:<br>%s<br>%s""" % (PAYLOAD, binascii.b2a_hex(PAYLOAD))

   EXPECTATION = """The connection is failed immediately, since the payload is not valid UTF-8."""

   def onOpen(self):

      self.expected[Case.OK] = []
      self.expectedClose = {"closedByMe":False,"closeCode":[self.p.CLOSE_STATUS_CODE_INVALID_PAYLOAD],"requireClean":False}
      self.p.sendMessage(self.PAYLOAD, binary = False)
      self.p.killAfter(1)
