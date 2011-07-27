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

   def onConnect(self, host, uri, origin, protocols):
      #print "Client connected", host, uri, origin, protocols
      pass

   def onOpen(self):
      #print "Connection now open."
      pass

   def onClose(self):
      #print "Client lost."
      pass

   def onMessage(self, msg, binary):
      if not binary:
         obj = json.loads(msg)
         print obj
         if obj[0] == "sendframe":
            pl = obj[1]["payload"].encode("UTF-8")
            self.sendFrame(opcode = obj[1]["opcode"], payload = pl, fin = obj[1]["fin"])


class FuzzingService(WebSocketService):

   def __init__(self, debug = False):
      self.debug = debug
      self.protocol = FuzzingServiceConnection

   def startFactory(self):
      pass

   def stopFactory(self):
      pass
