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

from autobahn.twisted.wamp import ApplicationSession



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

      def ping():
         return

      def add2(a, b):
         return a + b

      def stars(nick = "somebody", stars = 0):
         return "{} starred {}x".format(nick, stars)

      def orders(product, limit = 5):
         return ["Product {}".format(i) for i in range(50)][:limit]

      def arglen(*args, **kwargs):
         return [len(args), len(kwargs)]

      self.register(ping, 'com.arguments.ping')
      self.register(add2, 'com.arguments.add2')
      self.register(stars, 'com.arguments.stars')
      self.register(orders, 'com.arguments.orders')
      self.register(arglen, 'com.arguments.arglen')
