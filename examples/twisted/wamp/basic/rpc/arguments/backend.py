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

from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationSession



class Component(ApplicationSession):
   """
   An application component providing procedures with different kinds of arguments.
   """

   @inlineCallbacks
   def onJoin(self, details):
      print("session attached")

      def ping():
         return

      def add2(a, b):
         return a + b

      def stars(nick = "somebody", stars = 0):
         return u"{} starred {}x".format(nick, stars)

      def orders(product, limit = 5):
         return [u"Product {}".format(i) for i in range(50)][:limit]

      def arglen(*args, **kwargs):
         return [len(args), len(kwargs)]

      yield self.register(ping, u'com.arguments.ping')
      yield self.register(add2, u'com.arguments.add2')
      yield self.register(stars, u'com.arguments.stars')
      yield self.register(orders, u'com.arguments.orders')
      yield self.register(arglen, u'com.arguments.arglen')
      print("procedures registered")



if __name__ == '__main__':
   from autobahn.twisted.wamp import ApplicationRunner
   runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
   runner.run(Component)
