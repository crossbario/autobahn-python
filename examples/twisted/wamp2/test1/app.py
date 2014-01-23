###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
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

from twisted.internet.defer import inlineCallbacks

from autobahn.wamp.protocol import WampAppSession


class MyAppBackendSession(WampAppSession):
   """
   Example WAMP application backend.
   """

   def onSessionOpen(self, info):

      def add2(a, b):
         return a + b

      self.register(add2, 'com.myapp.add2')



class MyAppFrontendSession(WampAppSession):
   """
   Example WAMP application frontend.
   """

   @inlineCallbacks
   def onSessionOpen(self, info):

      res = yield self.call('com.myapp.add2', 2, 3)
      print("Result: {}".format(res))

      self.closeSession()


   def onSessionClose(self, reason, message):
      from twisted.internet import reactor
      reactor.stop()
