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
from asyncio import Protocol


class AdapterProtocol(Protocol):

   def connection_made(self, transport):
      peername = transport.get_extra_info('peername')
      print('connection from {}'.format(peername))
      self._protocol.transport = transport

   def data_received(self, data):
      self._protocol.data_received(data)
      #print('data received: {}'.format(data.decode()))
      #self.transport.write(data)
      #self.transport.close()


class AdapterFactory:

   def __init__(self, factory, loop = None):
      self._factory = factory

      if loop is None:
         loop = asyncio.get_event_loop()
      self._loop = loop


   def __call__(self):
      proto = AdapterProtocol()
      proto.factory = self
      proto._protocol = self._factory()
      print("asyncio protocol created")
      return proto
