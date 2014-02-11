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

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from autobahn.wamp.types import CallResult
from autobahn.twisted.wamp import ApplicationSession



class ComplexBackend(ApplicationSession):
   """
   Application component that provides procedures which
   return complex results.
   """

   def onConnect(self):
      self.join("realm1")


   def onJoin(self, details):

      def add_complex(a, ai, b, bi):
         return CallResult(c = a + b, ci = ai + bi)

      self.register(add_complex, 'com.myapp.add_complex')

      def split_name(fullname):
         forename, surname = fullname.split()
         return CallResult(forename, surname)

      self.register(split_name, 'com.myapp.split_name')



class ComplexFrontend(ApplicationSession):
   """
   Application component that calls procedures which
   produce complex results and showing how to access those.
   """

   def onConnect(self):
      self.join("realm1")


   @inlineCallbacks
   def onJoin(self, details):

      res = yield self.call('com.myapp.add_complex', 2, 3, 4, 5)
      print("Result: {} + {}i".format(res.kwresults['c'], res.kwresults['ci']))

      res = yield self.call('com.myapp.split_name', 'Homer Simpson')
      print("Forname: {}, Surname: {}".format(res.results[0], res.results[1]))

      self.leave()


   def onLeave(self, details):
      self.disconnect()


   def onDisconnect(self):
      reactor.stop()
