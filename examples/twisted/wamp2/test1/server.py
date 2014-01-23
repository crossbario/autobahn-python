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

from autobahn.wamp.protocol import WampAppSession, \
                                   WampRouterSessionFactory


class MyAppSession(WampAppSession):

   def onSessionOpen(self, info):
      print "MyEmbeddedSession.onSessionOpen", info.me, info.peer

      def onevent(*args, **kwargs):
         print "EVENT", args, kwargs

      self.subscribe(onevent, 'com.myapp.topic1')

      def add2(a, b):
         return a + b

      self.register(add2, 'com.myapp.add2')



if __name__ == '__main__':

   import sys

   from twisted.python import log
   from twisted.internet import reactor

   from autobahn.twisted.websocket import WampWebSocketServerFactory

   log.startLogging(sys.stdout)

   sessionFactory = WampRouterSessionFactory()
   sessionFactory.add(MyAppSession())

   transportFactory = WampWebSocketServerFactory(sessionFactory, "ws://localhost:9000", debug = False)
   transportFactory.setProtocolOptions(failByDrop = False)

   reactor.listenTCP(9000, transportFactory)
   reactor.run()
