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

from websocket import WebSocketService, WebSocketServiceConnection, HttpException
import json

class FuzzingServiceConnection(WebSocketServiceConnection):

   def onPong(self, payload):
      if self.debug:
         #print self.peer, "PONG received", unicode(payload, "UTF-8")
         print self.peer, "PONG received", payload

   def onMessage(self, msg, binary):
      if not binary:
         obj = json.loads(msg)
         if obj[0] == "sendframe":
            pl = obj[1].get("payload", "")
            self.sendFrame(opcode = obj[1]["opcode"],
                           payload = pl.encode("UTF-8"),
                           fin = obj[1].get("fin", True),
                           rsv = obj[1].get("rsv", 0),
                           mask = obj[1].get("mask", None))


class FuzzingService(WebSocketService):

   def __init__(self, debug = False):
      self.debug = debug
      self.protocol = FuzzingServiceConnection

   def startFactory(self):
      pass

   def stopFactory(self):
      pass
