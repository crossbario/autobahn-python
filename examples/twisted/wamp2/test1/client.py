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

from autobahn.wamp.protocol import WampProtocol


class MyAppSession(WampProtocol):

   def onSessionOpen(self, session_id, peer_session_id):
      print "MyAppSession.onSessionOpen", session_id, peer_session_id
      def add2(a, b):
         return a + b

      self.register(add2, 'com.myapp.add2')

   def onSessionClose(self):
      print "MyAppSession.onSessionOpen"


class MyAppSessionFactory:

   def __call__(self):
      return MyAppSession()


def makeSession():
   return MyAppSession()



if __name__ == '__main__':

   import sys

   from twisted.python import log
   from twisted.internet import reactor

   from autobahn.twisted import websocket

   log.startLogging(sys.stdout)

   sessionFactory = MyAppSessionFactory()

   transportFactory = websocket.WampClientFactory(sessionFactory, "ws://localhost:9000", debug = True)

   reactor.connectTCP("127.0.0.1", 9000, transportFactory)
   reactor.run()
