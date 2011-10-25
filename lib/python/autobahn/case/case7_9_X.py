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

## list of (payload length, message count, case timeout)
tests = [0,999,1004,1005,1006,1100,2000,5000,65535]

Case7_9_X = []

def __init__(self, protocol):
   Case.__init__(self, protocol)
   
def onConnectionLost(self, failedByMe):
      Case.onConnectionLost(self, failedByMe)
      
      if self.behaviorClose == Case.WRONG_CODE:
         self.behavior = Case.FAILED
         self.passed = False
         self.result = self.resultClose
         
def onOpen(self):
   self.expected[Case.OK] = []      
   self.expectedClose = {"failedByMe":True,"closeCode":[self.p.CLOSE_STATUS_CODE_PROTOCOL_ERROR],"requireClean":False}
   self.p.sendCloseFrame(self.CLOSE_CODE, reasonUtf8 = "")
   self.p.killAfter(1)

i = 1
for s in tests:
   DESCRIPTION = """Send close with close code %d""" % s
   EXPECTATION = """Clean close with normal or echoed code"""
   C = type("Case7_9_%d" % i,
			(object, Case, ),
			{"CLOSE_CODE": s,
			 "DESCRIPTION": """%s""" % DESCRIPTION,
			 "EXPECTATION": """%s""" % EXPECTATION,
			 "__init__": __init__,
			 "onOpen": onOpen,
			 "onConnectionLost": onConnectionLost,
			 })
   Case7_9_X.append(C)
   i += 1
