###############################################################################
##
##  Copyright 2012 Tavendo GmbH
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

from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampCraClientProtocol


class MyClientProtocol(WampCraClientProtocol):
   """
   Authenticated WAMP client using WAMP-Challenge-Response-Authentication ("WAMP-CRA").
   """

   def onSessionOpen(self):
      ## "authenticate" as anonymous
      ##
      #self.authenticate(self.onAuthSuccess, self.onAuthError)

      ## authenticate as "foobar" with password "secret"
      ##
      self.authenticate(self.onAuthSuccess,
                        self.onAuthError,
                        authKey = "foobar",
                        authExtra = None,
                        authSecret = "secret")


   def onClose(self, wasClean, code, reason):
      reactor.stop()

   def onAuthSuccess(self, permissions):
      print "Authentication Success!", permissions
      self.publish("http://example.com/topics/mytopic1", "Hello, world!")
      self.sendClose()

   def onAuthError(self, uri, desc, details):
      print "Authentication Error!", uri, desc, details
      self.sendClose()


if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   log.startLogging(sys.stdout)
   factory = WampClientFactory("ws://localhost:9000", debugWamp = debug)
   factory.protocol = MyClientProtocol
   connectWS(factory)
   reactor.run()
