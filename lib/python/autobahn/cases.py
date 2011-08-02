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

from websocket import WebSocketProtocol
from twisted.python import log
import pickle


class Case:

   def __init__(self, protocol):
      self.p = protocol
      self.passed = True
      self.result = "Ok"
      self.init()

   def compare(self, obj1, obj2):
      return pickle.dumps(obj1) == pickle.dumps(obj2)

   def init(self):
      pass

   def onOpen(self):
      pass

   def onMessage(self, msg, binary):
      pass

   def onPing(self, payload):
      pass

   def onPong(self, payload):
      pass

   def onClose(self, code, reason):
      pass


from case1 import Case1
from case2 import Case2

Cases = [Case1, Case2]
