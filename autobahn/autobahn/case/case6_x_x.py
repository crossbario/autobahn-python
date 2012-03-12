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
from autobahn.utf8validator import UTF8_TEST_SEQUENCES


Case6_X_X = []
Case6_X_X_CaseSubCategories = {}


def __init__(self, protocol):
   Case.__init__(self, protocol)

def onOpen(self):

   if self.isValid:
      self.expected[Case.OK] = [("message", self.PAYLOAD, False)]
      self.expectedClose = {"closedByMe":True,"closeCode":[self.p.CLOSE_STATUS_CODE_NORMAL],"requireClean":True}
   else:
      self.expected[Case.OK] = []
      self.expectedClose = {"closedByMe":False,"closeCode":[self.p.CLOSE_STATUS_CODE_INVALID_PAYLOAD],"requireClean":False}

   self.p.sendMessage(self.PAYLOAD, binary = False)
   self.p.killAfter(0.5)

i = 5
for t in UTF8_TEST_SEQUENCES:
   j = 1
   Case6_X_X_CaseSubCategories["6.%d" % i] = t[0]
   for p in t[1]:
      if p[0]:
         desc = "Send a text message with payload which is valid UTF-8 in one fragment."
         exp = "The message is echo'ed back to us."
      else:
         desc = "Send a text message with payload which is not valid UTF-8 in one fragment."
         exp = "The connection is failed immediately, since the payload is not valid UTF-8."
      C = type("Case6_%d_%d" % (i, j),
                (object, Case, ),
                {"PAYLOAD": p[1],
                 "isValid": p[0],
                 "DESCRIPTION": """%s<br><br>MESSAGE:<br>%s<br>%s""" % (desc, p[1], binascii.b2a_hex(p[1])),
                 "EXPECTATION": """%s""" % exp,
                 "__init__": __init__,
                 "onOpen": onOpen})
      Case6_X_X.append(C)
      j += 1
   i += 1

