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
from twisted.internet import reactor
from autobahn.websocket import listenWS
from autobahn.wamp import exportRpc, WampServerFactory, WampServerProtocol


class KeyValue:
   """
   Simple, persistent key-value store.
   """

   def __init__(self, filename):
      self.store = shelve.open(filename)

   @exportRpc
   def set(self, key = None, value = None):
      if key is not None:
         k = str(key)
         if value is not None:
            self.store[k] = value
         else:
            if self.store.has_key(k):
               del self.store[k]
      else:
         self.store.clear()

   @exportRpc
   def get(self, key = None):
      if key is None:
         return self.store.items()
      else:
         return self.store.get(str(key), None)

   @exportRpc
   def keys(self):
      return self.store.keys()


class KeyValueServerProtocol(WampServerProtocol):
   """
   Demonstrates creating a server with Autobahn WebSockets that provides
   a persistent key-value store which can we access via RPCs.
   """

   def onSessionOpen(self):
      ## register the key-value store, which resides on the factory within
      ## this connection
      self.registerForRpc(self.factory.keyvalue, "http://example.com/simple/keyvalue#")


class KeyValueServerFactory(WampServerFactory):

   protocol = KeyValueServerProtocol

   def __init__(self, url):
      WampServerFactory.__init__(self, url)

      ## the key-value store resides on the factory object, since it is to
      ## be shared among all client connections
      self.keyvalue = KeyValue("keyvalue.dat")


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = KeyValueServerFactory("ws://localhost:9000")
   listenWS(factory)
   reactor.run()
