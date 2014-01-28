###############################################################################
##
##  Copyright (C) 2012-2013 Tavendo GmbH
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
from pprint import pprint

from twisted.python import log
from twisted.internet import reactor

from autobahn.twisted.websocket import connectWS

from autobahn.wamp1.protocol import WampClientFactory, \
                                    WampCraClientProtocol



class MyClientProtocol(WampCraClientProtocol):
   """
   Authenticated WAMP client using WAMP-Challenge-Response-Authentication ("WAMP-CRA").
   """

   def onSessionOpen(self):
      ## "authenticate" as anonymous
      ##
      #d = self.authenticate()

      ## authenticate as "foobar" with password "secret"
      ##
      d = self.authenticate(authKey = "foobar",
                            authExtra = None,
                            authSecret = "secret")

      d.addCallbacks(self.onAuthSuccess, self.onAuthError)


   def onClose(self, wasClean, code, reason):
      reactor.stop()


   def onAuthSuccess(self, permissions):
      print "Authentication Success!", permissions
      self.publish("http://example.com/topics/mytopic1", "Hello, world!")
      d = self.call("http://example.com/procedures/hello", "Foobar")
      d.addBoth(pprint)
      d.addBoth(self.sendClose)


   def onAuthError(self, e):
      uri, desc, details = e.value.args
      print "Authentication Error!", uri, desc, details



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
