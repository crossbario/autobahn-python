###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
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

from __future__ import absolute_import

from autobahn.wamp.protocol import WampAppSession

from twisted.internet import reactor

class MyAppSession(WampAppSession):

   def onSessionOpen(self, info):
      print "MyAppSession.onSessionOpen", info.me, info.peer

      def add2(a, b):
         return a + b

      self.register(add2, 'com.myapp.add2')

      def onevent(*args, **kwargs):
         print "EVENT", args, kwargs

      self.subscribe(onevent, 'com.myapp.topic1')

      def pub():
         self.publish('com.myapp.topic1', "Hello from")
#         self.publish('com.myapp.topic1', "Hello from {}".format(self.factory._name))
         reactor.callLater(1, pub)

      pub()

      #def close():
      #   self.closeSession('com.myapp.shutdown_in_progress', 'We are doing maintenance')

      #reactor.callLater(2, close)

   def onSessionClose(self, reason, message):
      print "MyAppSession.onSessionOpen", reason, message


class MyAppSessionFactory:

   def __init__(self, name = "unknown"):
      self._name = name

   def __call__(self):
      session = MyAppSession()
      session.factory = self
      return session


def makeSession():
   return MyAppSession()


def makeFactory(klass):
   def create():
      return klass()
   return create


class WampAppFactory:

   def __call__(self):
      session = self.session()
      session.factory = self
      return session


if __name__ == '__main__':

   import sys

   from twisted.python import log
   from twisted.internet import reactor

   from autobahn.twisted.websocket import WampWebSocketClientFactory

   log.startLogging(sys.stdout)

   name = "unknown"
   if len(sys.argv) > 1:
      name = sys.argv[1]

   sessionFactory = WampAppFactory()
   sessionFactory.session = MyAppSession
#   sessionFactory = makeFactory(MyAppSession)
#   sessionFactory = MyAppSessionFactory(name)

   transportFactory = WampWebSocketClientFactory(sessionFactory, "ws://localhost:9000", debug = False)
   transportFactory.setProtocolOptions(failByDrop = False)

   reactor.connectTCP("127.0.0.1", 9000, transportFactory)
   reactor.run()
