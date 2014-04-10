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

from autobahn import wamp
from autobahn.wamp.exception import ApplicationError
from autobahn.twisted.wamp import ApplicationSession



@wamp.error("com.myapp.error1")
class AppError1(Exception):
   """
   An application specific exception that is decorated with a WAMP URI,
   and hence can be automapped by Autobahn.
   """



class Component(ApplicationSession):
   """
   Example WAMP application frontend that catches exceptions.
   """

   @inlineCallbacks
   def onJoin(self, details):

      ## catching standard exceptions
      ##
      for x in [2, 0, -2]:
         try:
            res = yield self.call('com.myapp.sqrt', x)
         except Exception as e:
            print("Error: {} {}".format(e, e.args))
         else:
            print("Result: {}".format(res))


      ## catching WAMP application exceptions
      ##
      for name in ['foo', 'a', '*'*11, 'Hello']:
         try:
            res = yield self.call('com.myapp.checkname', name)
         except ApplicationError as e:
            print("Error: {} {} {} {}".format(e, e.error, e.args, e.kwargs))
         else:
            print("Result: {}".format(res))


      ## defining and automapping WAMP application exceptions
      ##
      self.define(AppError1)

      try:
         yield self.call('com.myapp.compare', 3, 17)
      except AppError1 as e:
         print("Compare Error: {}".format(e))


      self.leave()


   def onDisconnect(self):
      reactor.stop()
