###############################################################################
##
##  Copyright (C) 2013 Tavendo GmbH
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


from autobahn.wamp2.broker import Broker
from autobahn.wamp2.websocket import WampWebSocketServerProtocol, \
                                     WampWebSocketServerFactory

from autobahn.wamp2.serializer import WampJsonSerializer, WampMsgPackSerializer

from autobahn.wamp2.http import WampHttpResourceSession, \
                                WampHttpResource


from autobahn.wamp2.protocol import WampProtocol


class MyWampSession(WampProtocol):

   def __init__(self, broker):
      self._broker = broker

   def onSessionOpen(self):
      self.setBroker(self._broker)


class MyWampSessionFactory:

   def __init__(self):
      self._broker = Broker()

   def createSession(self):
      session = MyWampSession(self._broker)
      return session



class MyPubSubResourceSession(WampHttpResourceSession):

   def onSessionOpen(self):
      self.setBroker(self._parent._broker)

   def onSessionClose(self):
      print "SESSION CLOSED"


class MyPubSubResource(WampHttpResource):

   protocol = MyPubSubResourceSession

   def __init__(self, serializers, broker, debug = True):
      WampHttpResource.__init__(self, serializers = serializers, debug = debug)
      self._broker = broker



class PubSubServerProtocol(WampWebSocketServerProtocol):

   def onSessionOpen(self):
      self.setBroker(self.factory._broker)



class PubSubServerFactory(WampWebSocketServerFactory):

   protocol = PubSubServerProtocol

   def __init__(self, url, serializers, broker, debug = False):
      WampWebSocketServerFactory.__init__(self, url, serializers = serializers, debug = debug)
      self._broker = broker




if __name__ == '__main__':

   import sys

   from twisted.internet import reactor
   from twisted.python import log
   from twisted.web.server import Site
   from twisted.web.static import File

   from twisted.internet.endpoints import serverFromString

   log.startLogging(sys.stdout)

   broker = Broker()

   jsonSerializer = WampJsonSerializer()

   serializers = [WampMsgPackSerializer(), jsonSerializer]

   wampfactory = PubSubServerFactory("ws://localhost:9000", serializers, broker, debug = False)
   wampserver = serverFromString(reactor, "tcp:9000")
   wampserver.listen(wampfactory)


   wampResource = MyPubSubResource([jsonSerializer], broker)

   root = File("longpoll")
   root.putChild("wamp", wampResource)

   site = Site(root)
   site.log = lambda _: None # disable any logging
   reactor.listenTCP(8080, site)

   reactor.run()
