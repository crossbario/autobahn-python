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

from __future__ import absolute_import
from twisted.internet.protocol import Protocol, Factory


class AdapterProtocol(Protocol):

   def connectionMade(self):
      peername = str(self.transport.getPeer())
      print('connection from {}'.format(peername))
      self._protocol.transport = self.transport

   def dataReceived(self, data):
      self._protocol.data_received(data)
      #print('data received: {}'.format(data.decode()))
      #self.transport.write(data)
      #self.transport.loseConnection()


class AdapterFactory(Factory):

   def __init__(self, factory, reactor = None):
      self._factory = factory

      ## lazy import to avoid reactor install upon module import
      if reactor is None:
         from twisted.internet import reactor
      self._reactor = reactor


   def buildProtocol(self, addr):
      proto = AdapterProtocol()
      proto.factory = self
      proto._protocol = self._factory()
      print("twisted protocol created")
      return proto
