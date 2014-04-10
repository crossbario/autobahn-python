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

import asyncio

from autobahn.asyncio.wamp import ApplicationSession



class Component(ApplicationSession):
   """
   An application component using the time service
   during 3 subsequent WAMP sessions, while the
   underlying transport continues to exist.
   """

   def __init__(self, config):
      ApplicationSession.__init__(self, config)
      self.count = 0


   @asyncio.coroutine
   def onJoin(self, details):
      print("Realm joined (WAMP session started).")

      try:
         now = yield from self.call('com.timeservice.now')
      except Exception as e:
         print("Error: {}".format(e))
      else:
         print("Current time from time service: {}".format(now))

      self.leave()


   def onLeave(self, details):
      print("Realm left (WAMP session ended).")
      self.count += 1
      if self.count < 3:
         self.join("realm1")
      else:
         self.disconnect()


   def onDisconnect(self):
      print("Transport disconnected.")
      asyncio.get_event_loop().stop()
