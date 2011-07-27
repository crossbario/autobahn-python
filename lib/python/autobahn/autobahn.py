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

class AutobahnServiceConnection(WebSocketServiceConnection):

   def onConnect(self, host, uri, origin, protocols):
      print "Client connected", host, uri, origin, protocols
      #raise HttpException(401, "Authenticate first!")

   def onOpen(self):
      print "Connection now open."
#      self.initial_ping_payload = ''.join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_") for i in range(16)])
#      self.initial_pong_received = False
#      self.sendPing(self.initial_ping_payload);

   def onPing(self, payload):
      print "PING received : ", str(payload)
      self.sendPong(payload)


   def onPong(self, payload):
      print "PONG received : ", str(payload)
      if not self.initial_pong_received:
         if payload == self.initial_ping_payload:
            #print "initial ping/pong finished!"
            self.initial_pong_received = True
            self.onOpen()
         else:
            pass
            #print "initial ping/pong failure"

   def onClose(self):
      print "Client lost."

   def onMessage(self, msg, binary):
      try:
         obj = json.loads(msg)
      except:
         print "could not parse JSON"
         print msg
#      self.sendCloseFrame(WebSocketServiceConnection.CLOSE_STATUS_CODE_PROTOCOL_ERROR, "data frame using reserved opcode")
#      self.sendCloseFrame(3000, "data frame using reserved opcode")
      res = {"name": "Tobias", "age": 38}
      self.sendMessage(json.dumps(res))


class AutobahnService(WebSocketService):

   def __init__(self):
      self.protocol = AutobahnServiceConnection

   def startFactory(self):
      pass

   def stopFactory(self):
      pass
