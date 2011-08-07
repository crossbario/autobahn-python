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

   def __init__(self, protocol):
      self.p = protocol
      self.received = []
      self.expected = []
      self.init()

   def init(self):
      pass

   def onOpen(self):
      pass

   def onMessage(self, msg, binary):
      self.received.append(("message", msg, binary))

   def onPing(self, payload):
      self.received.append(("ping", payload))

   def onPong(self, payload):
      self.received.append(("pong", payload))

   def onClose(self, code, reason):
      pass

   def compare(self, obj1, obj2):
      return pickle.dumps(obj1) == pickle.dumps(obj2)

   def onConnectionLost(self, failedByMe):
      self.received.append(("failedByMe", failedByMe))
      self.passed = self.compare(self.received, self.expected)
      if self.passed:
         self.result = "Ok, actual events match expected."
      else:
         self.result = "Failure, actual events differ from expected."
