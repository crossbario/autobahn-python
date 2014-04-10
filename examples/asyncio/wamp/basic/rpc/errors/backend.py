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

import asyncio

from autobahn import wamp
from autobahn.wamp.exception import ApplicationError
from autobahn.asyncio.wamp import ApplicationSession



@wamp.error("com.myapp.error1")
class AppError1(Exception):
   """
   An application specific exception that is decorated with a WAMP URI,
   and hence can be automapped by Autobahn.
   """



class Component(ApplicationSession):
   """
   Example WAMP application backend that raised exceptions.
   """

   def __init__(self, realm = "realm1"):
      ApplicationSession.__init__(self)
      self._realm = realm


   def onConnect(self):
      self.join(self._realm)


   def onJoin(self, details):

      ## raising standard exceptions
      ##
      def sqrt(x):
         if x == 0:
            raise Exception("don't ask folly questions;)")
         else:
            ## this also will raise, if x < 0
            return math.sqrt(x)

      self.register(sqrt, 'com.myapp.sqrt')


      ## raising WAMP application exceptions
      ##
      def checkname(name):
         if name in ['foo', 'bar']:
            raise ApplicationError("com.myapp.error.reserved")

         if name.lower() != name.upper():
            ## forward positional arguments in exceptions
            raise ApplicationError("com.myapp.error.mixed_case", name.lower(), name.upper())

         if len(name) < 3 or len(name) > 10:
            ## forward keyword arguments in exceptions
            raise ApplicationError("com.myapp.error.invalid_length", min = 3, max = 10)

      self.register(checkname, 'com.myapp.checkname')


      ## defining and automapping WAMP application exceptions
      ##
      self.define(AppError1)

      def compare(a, b):
         if a < b:
            raise AppError1(b - a)

      self.register(compare, 'com.myapp.compare')
