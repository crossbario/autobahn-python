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

import random

try:
   import asyncio
except ImportError:
   ## Trollius >= 0.3 was renamed
   import trollius as asyncio

from autobahn.wamp.types import SubscribeOptions
from autobahn.asyncio.wamp import ApplicationSession



class Component(ApplicationSession):
   """
   An application component that publishes events with no payload
   and with complex payloads every second.
   """

   @asyncio.coroutine
   def onJoin(self, details):

      counter = 0
      while True:
         self.publish('com.myapp.heartbeat')

         obj = {'counter': counter, 'foo': [1, 2, 3]}
         self.publish('com.myapp.topic2', random.randint(0, 100), 23, c = "Hello", d = obj)

         counter += 1
         yield from asyncio.sleep(1)
