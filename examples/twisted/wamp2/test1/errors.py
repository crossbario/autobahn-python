###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
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

import math

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from autobahn.wamp.protocol import WampAppSession



class ErrorsTestBackend(WampAppSession):
   """
   Example WAMP application backend.
   """

   def onSessionOpen(self, details):

      def sqrt(x):
         if x < 0:
            raise Exception("cannot take sqrt of negative number")
         else:
            return math.sqrt(x)

      self.register(sqrt, 'com.myapp.sqrt')



class ErrorsTestFrontend(WampAppSession):
   """
   Example WAMP application frontend.
   """

   @inlineCallbacks
   def onSessionOpen(self, info):

      for x in [2, 0, -2]:
         try:
            res = yield self.call('com.myapp.sqrt', x)
         except Exception as e:
            print("Error: {}".format(e))
         else:
            print("Result: {}".format(res))

      self.closeSession()


   def onSessionClose(self, details):
      reactor.stop()
