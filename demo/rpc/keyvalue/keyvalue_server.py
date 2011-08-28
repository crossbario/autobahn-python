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

import sys, shelve
from twisted.python import log
from twisted.internet import reactor, defer
from autobahn.autobahn import exportRpc, AutobahnServerFactory, AutobahnServerProtocol


class KeyValue:
   """
   Simple, persistent key-value store.
   """

   def __init__(self, filename):
      self.store = shelve.open(filename)

   @exportRpc
   def set(self, key, value):
      k = str(key)
      if value:
         self.store[k] = value
      else:
         if self.store.has_key(k):
            del self.store[k]

   @exportRpc
   def get(self, key):
      return self.store.get(str(key), None)

   @exportRpc
   def keys(self):
      return self.store.keys()


class KeyValueServerProtocol(AutobahnServerProtocol):
   """
   Demonstrates creating a server with Autobahn WebSockets that provides
   a persistent key-value store which can we access via RPCs.
   """

   def onConnect(self, connectionRequest):
      ## register the key-value store, which resides on the factory within
      ## this connection
      self.registerForRpc(self.factory.keyvalue, "http://example.com/simple/keyvalue#")


class KeyValueServerFactory(AutobahnServerFactory):

   protocol = KeyValueServerProtocol

   def __init__(self, debug = False):
      AutobahnServerFactory.__init__(self, debug)

      ## the key-value store resides on the factory object, since it is to
      ## be shared among all client connections
      self.keyvalue = KeyValue("keyvalue.dat")


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = KeyValueServerFactory(debug = False)
   reactor.listenTCP(9000, factory)
   reactor.run()
