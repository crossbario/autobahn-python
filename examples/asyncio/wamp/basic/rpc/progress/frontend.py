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

from autobahn.wamp.types import CallOptions, RegisterOptions
from autobahn.asyncio.wamp import ApplicationSession



class Component(ApplicationSession):
   """
   Application component that consumes progressive results.
   """

   @asyncio.coroutine
   def onJoin(self, details):

      def on_progress(i):
         print("Progress: {}".format(i))

      res = yield from self.call('com.myapp.longop', 3, options = CallOptions(onProgress = on_progress))

      print("Final: {}".format(res))

      self.leave()


   def onDisconnect(self):
      asyncio.get_event_loop().stop()
