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

import datetime

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession

from twisted.internet.defer import inlineCallbacks


class Component(ApplicationSession):
   """
   An application component registering RPC endpoints using decorators.
   """

   def __init__(self, realm = "realm1"):
      ApplicationSession.__init__(self)
      self._realm = realm


   def onConnect(self):
      self.join(self._realm)


   @inlineCallbacks
   def onJoin(self, details):

      ## register all methods on this object decorated with "@wamp.procedure"
      ## as a RPC endpoint
      ##
      regs = yield self.register(self)
      for r in regs:
         if r[0]:
            print("Ok, registered procedure with registration ID {}".format(r[1].id))
         else:
            print("Failed to register procedure: {}".format(r[1].value))


   @wamp.procedure('com.mathservice.add2')
   def add2(self, x, y):
      return x + y


   @wamp.procedure('com.mathservice.mul2')
   def mul2(self, x, y):
      return x * y


   @wamp.procedure('com.mathservice.div2')
   def square(self, x, y):
      if y:
         return float(x) / float(y)
      else:
         return 0
