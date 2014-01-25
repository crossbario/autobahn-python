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

from twisted.internet import reactor
from twisted.internet.defer import Deferred, \
                                   inlineCallbacks, \
                                   returnValue

from autobahn.wamp.protocol import WampAppSession
from autobahn.wamp.types import CallOptions, CallResult, RegisterOptions



def sleep(delay):
   d = Deferred()
   reactor.callLater(delay, d.callback, None)
   return d


class MyAppBackendSession(WampAppSession):
   """
   Example WAMP application backend.
   """

   def onSessionOpen(self, info):

      @inlineCallbacks
      def add2(a, b, details = None):
         print details.progress
         if a > 5:
            raise Exception("number too large")
         else:
            if details.progress:
               for i in range(3):
                  details.progress(i)
                  yield sleep(1)
            else:
               yield sleep(1)
            #returnValue(a + b)
            returnValue(CallResult(a, b, result = a + b))

      def add2b(a, b):
         return a + b

      self.register(add2, 'com.myapp.add2', RegisterOptions(details = 'details'))


   def onSessionClose(self, reason, message):      
      reactor.stop()



class MyAppFrontendSession(WampAppSession):
   """
   Example WAMP application frontend.
   """

   @inlineCallbacks
   def onSessionOpen(self, info):

      def onprogress(i):
         print "onprogress", i

      try:
         #res = yield self.call('com.myapp.add2', 15, 3)
         res = yield self.call('com.myapp.add2', 2, 3, options = CallOptions(timeout = 5000, onProgress = onprogress))
      except Exception as e:
         print("Error: {}".format(e))
      else:
         print("Result: {}".format(res))

      self.closeSession()


   def onSessionClose(self, reason, message):      
      reactor.stop()
