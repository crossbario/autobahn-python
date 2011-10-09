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

import sys
from twisted.python import log
from twisted.internet import reactor
from autobahn.wamp import WampClientFactory, WampClientProtocol


class KeyValueClientProtocol(WampClientProtocol):

   def done(self, *args):
      self.sendClose()

   def show(self, key, value):
      print key, value

   def get(self, keys):
      for key in keys:
         self.call("keyvalue:get", key).addCallback(lambda value, key = key: self.show(key, value))

   def onOpen(self):
      self.prefix("keyvalue", "http://example.com/simple/keyvalue#")
      self.call("keyvalue:keys").addCallbacks(self.get).addCallback(self.done)


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = WampClientFactory(debug = False)
   factory.protocol = KeyValueClientProtocol
   reactor.connectTCP("localhost", 9000, factory)
   reactor.run()
