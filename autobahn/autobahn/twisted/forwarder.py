###############################################################################
##
##  Copyright (C) 2013 Tavendo GmbH
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

from twisted.python import usage
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import clientFromString, serverFromString
from twisted.application import service


class EndpointForwardingProtocol(Protocol):

   @inlineCallbacks
   def connectionMade(self):
      print("connectionMade")
      self.transport.write('how are you?')

   def dataReceived(self, data):
      print("dataReceived: {}".format(data))



class EndpointForwardingService(service.Service):

   def __init__(self, endpointDescriptor, destEndpointDescriptor, reactor = None):
      if reactor is None:
         from twisted.internet import reactor
      self._reactor = reactor
      self._endpointDescriptor = endpointDescriptor
      self._destEndpointDescriptor = destEndpointDescriptor

   @inlineCallbacks
   def startService(self):
      factory = Factory.forProtocol(EndpointForwardingProtocol)
      factory.service = self
      self._endpoint = serverFromString(self._reactor, self._endpointDescriptor)
      self._endpointPort = yield self._endpoint.listen(factory)

   def stopService(self):
      return self._endpointPort.stopListening()



class Options(usage.Options):
   synopsis = "[options]"
   longdesc = 'Endpoint Forwarder.'
   optParameters = [
      ["endpoint", "e", None, "Source endpoint."],
      ["dest_endpoint", "d", None,"Destination endpoint."]
   ]



def makeService(config):
   service = EndpointForwardingService(config['endpoint'], config['dest_endpoint'])
   return service
