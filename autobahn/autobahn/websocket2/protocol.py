###############################################################################
##
##  Copyright 2011-2013 Tavendo GmbH
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

class WebSocketServerProtocol:

   def data_received(self, data):
      print('data received: {}'.format(data.decode()))
      self.onMessage(data, False)

   def onMessage(self, payload, isBinary):
      pass

   def sendMessage(self, payload, isBinary = False):
      self.transport.write(payload)


class WebSocketServerFactory:

   protocol = WebSocketServerProtocol

   def __call__(self):
      proto = self.protocol()
      proto.factory = self
      return proto
