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

from autobahn.websocket import WebSocketProtocol
from twisted.python import log
import pickle
import textwrap


class Case:

   FAILED = "FAILED"
   OK = "OK"
   NON_STRICT = "NON-STRICT"
   WRONG_CODE = "WRONG CODE"
   UNCLEAN = "UNCLEAN"
   FAILED_BY_CLIENT = "FAILED BY CLIENT"
   INFORMATIONAL = "INFORMATIONAL"
   
   # to remove
   NO_CLOSE = "NO_CLOSE"
   
   SUBCASES = []

   def __init__(self, protocol):
      self.p = protocol
      self.received = []
      self.expected = {}
      self.expectedClose = {}
      self.behavior = Case.FAILED
      self.behaviorClose = Case.FAILED
      self.result = "Actual events differ from any expected."
      self.resultClose = "TCP connection was dropped without close handshake"
      self.reportTime = False
      self.subcase = None
      self.suppressClose = False # suppresses automatic close behavior (used in cases that deliberately send bad close behavior)
      self.init()

   def getSubcaseCount(self):
      return len(Case.SUBCASES)

   def setSubcase(self, subcase):
      self.subcase = subcase

   def init(self):
      pass

   def onOpen(self):
      pass

   def onMessage(self, msg, binary):
      self.received.append(("message", msg, binary))
      self.finishWhenDone()

   def onPing(self, payload):
      self.received.append(("ping", payload))
      self.finishWhenDone()

   def onPong(self, payload):
      self.received.append(("pong", payload))
      self.finishWhenDone()
   
   def onClose(self, wasClean, code, reason):
      pass
   
   def compare(self, obj1, obj2):
      return pickle.dumps(obj1) == pickle.dumps(obj2)

   def onConnectionLost(self, failedByMe):
      # check if we passed the test
      for e in self.expected:
         if self.compare(self.received, self.expected[e]):
            self.behavior = e
            self.passed = True
            self.result = "Actual events match at least one expected."
            break
      # check the close status
      if self.expectedClose["closedByMe"] != self.p.closedByMe:
         self.behaviorClose = Case.FAILED
         self.resultClose = "The connection was failed by the wrong endpoint"
      elif self.expectedClose["requireClean"] and not self.p.wasClean:
         self.behaviorClose = Case.UNCLEAN
         self.resultClose = "The spec requires the connection to be failed cleanly here"
      elif self.p.remoteCloseCode != None and self.p.remoteCloseCode not in self.expectedClose["closeCode"]:
         self.behaviorClose = Case.WRONG_CODE
         self.resultClose = "The close code should have been %s or empty" % ','.join(map(str,self.expectedClose["closeCode"]))
      elif not self.p.isServer and self.p.droppedByMe:
         self.behaviorClose = Case.FAILED_BY_CLIENT
         self.resultClose = "It is preferred that the server close the TCP connection"
      else:
         self.behaviorClose = Case.OK
         self.resultClose = "Connection was properly closed"

   def finishWhenDone(self):
      # if we match at least one expected outcome check if we are supposed to 
      # start the closing handshake and if so, do it.
      for e in self.expected:
         if not self.compare(self.received, self.expected[e]):
            return
      if self.expectedClose["closedByMe"] and not self.suppressClose:
         self.p.sendClose(self.expectedClose["closeCode"][0])
               
