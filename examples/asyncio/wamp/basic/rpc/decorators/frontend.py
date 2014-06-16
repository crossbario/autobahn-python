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

try:
   import asyncio
except ImportError:
   ## Trollius >= 0.3 was renamed
   import trollius as asyncio

from autobahn.asyncio.wamp import ApplicationSession



class Component(ApplicationSession):
   """
   An application component calling the different backend procedures.
   """

   @asyncio.coroutine
   def onJoin(self, details):

      procs = [u'com.mathservice.add2',
               u'com.mathservice.mul2',
               u'com.mathservice.div2']

      try:
         for proc in procs:
            res = yield from self.call(proc, 2, 3)
            print("{}: {}".format(proc, res))
      except Exception as e:
         print("Something went wrong: {}".format(e))

      self.leave()


   def onDisconnect(self):
      asyncio.get_event_loop().stop()
