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

import asyncio

from autobahn.wamp.types import CallOptions, RegisterOptions, PublishOptions
from autobahn.asyncio.wamp import ApplicationSession



class Component(ApplicationSession):
   """
   An application component providing procedures with
   different kinds of arguments.
   """

   def __init__(self, realm = "realm1"):
      ApplicationSession.__init__(self)
      self._realm = realm


   def onConnect(self):
      self.join(self._realm)


   def onJoin(self, details):

      def square(val, details = None):
         print("square called from: {}".format(details.caller))

         if val < 0:
            self.publish('com.myapp.square_on_nonpositive', val)
         elif val == 0:
            if details.caller:
               options = PublishOptions(exclude = [details.caller])
            else:
               options = None
            self.publish('com.myapp.square_on_nonpositive', val, options = options)
         return val * val

      self.register(square, 'com.myapp.square', RegisterOptions(details_arg = 'details'))
