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

import asyncio

from autobahn.websocket2 import protocol



class WebSocketServerProtocol(asyncio.Protocol, protocol.WebSocketServerProtocol):

   def connection_made(self, transport):
      self.transport = transport
      peername = transport.get_extra_info('peername')
      print('connection from {}'.format(peername))

   def data_received(self, data):
      self._onData(data)
      #print('data received: {}'.format(data.decode()))
      #self.transport.write(data)
      #self.transport.close()



class WebSocketServerFactory(protocol.WebSocketServerFactory):

   protocol = WebSocketServerProtocol

   def __init__(self, loop = None):

      if loop is None:
         loop = asyncio.get_event_loop()
      self._loop = loop


   def __call__(self):
      proto = self.protocol()
      proto.factory = self
      return proto
