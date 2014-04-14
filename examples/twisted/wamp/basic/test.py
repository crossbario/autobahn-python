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

import sys
import io
import six
import datetime

from twisted.python import log
from twisted.internet.defer import inlineCallbacks, Deferred, DeferredList
from twisted.internet.endpoints import serverFromString

from autobahn.wamp import router
from autobahn.twisted.util import sleep
from autobahn.twisted import wamp, websocket


class CaseComponent(wamp.ApplicationSession):
   """
   Application code goes here. This is an example component that calls
   a remote procedure on a WAMP peer, subscribes to a topic to receive
   events, and then stops the world after some events.
   """

   def __init__(self, config, done):
      wamp.ApplicationSession.__init__(self, config)
      self._done = done
      self.stop = False
      self._logline = 1
      self.finished = False

   def log(self, *args):
      if len(args) > 1:
         sargs = ", ".join(str(s) for s in args)
      elif len(args) == 1:
         sargs = args[0]
      else:
         sargs = "-"

      msg = u'= : {:>3} : {:<20} : {}'.format(self._logline, self.__class__.__name__, sargs)
      self._logline += 1
      print(msg)
      if self.config.log and not self.config.log.closed:
         self.config.log.write(msg + "\n")
         self.config.log.flush()
      else:
         print("log already closed")

   def finish(self):
      if not self.finished:
         self._done.callback(None)
         #self.disconnect()
         self.finished = True
      else:
         print("already finished")



class Case1_Backend(CaseComponent):

   @inlineCallbacks
   def onJoin(self, details):

      self.log("joined")

      def add2(x, y):
         self.log("add2 invoked: {}, {}".format(x, y))
         return x + y

      yield self.register(add2, 'com.mathservice.add2')
      self.log("add2 registered")

      self.finish()



class Case1_Frontend(CaseComponent):

   @inlineCallbacks
   def onJoin(self, details):

      self.log("joined")

      try:
         res = yield self.call('com.mathservice.add2', 2, 3)
      except Exception as e:
         self.log("call error: {}".format(e))
      else:
         self.log("call result: {}".format(res))

      self.finish()



class Case2_Backend(CaseComponent):

   @inlineCallbacks
   def onJoin(self, details):

      self.log("joined")

      def ping():
         self.log("ping() is invoked")
         return

      def add2(a, b):
         self.log("add2() is invoked", a, b)
         return a + b

      def stars(nick = "somebody", stars = 0):
         self.log("stars() is invoked", nick, stars)
         return u"{} starred {}x".format(nick, stars)

      def orders(product, limit = 5):
         self.log("orders() is invoked", product, limit)
         return [u"Product {}".format(i) for i in range(50)][:limit]

      def arglen(*args, **kwargs):
         self.log("arglen() is invoked", args, kwargs)
         return [len(args), len(kwargs)]

      yield self.register(ping, u'com.arguments.ping')
      yield self.register(add2, u'com.arguments.add2')
      yield self.register(stars, u'com.arguments.stars')
      yield self.register(orders, u'com.arguments.orders')
      yield self.register(arglen, u'com.arguments.arglen')

      self.log("procedures registered")

      self.finish()


from autobahn.twisted.util import sleep

class Case2_Frontend(CaseComponent):

   @inlineCallbacks
   def onJoin(self, details):

      self.log("joined")

      #yield sleep(3)

      yield self.call(u'com.arguments.ping')
      self.log("Pinged!")

      res = yield self.call(u'com.arguments.add2', 2, 3)
      self.log("Add2: {}".format(res))

      starred = yield self.call(u'com.arguments.stars')
      self.log("Starred 1: {}".format(starred))

      starred = yield self.call(u'com.arguments.stars', nick = u'Homer')
      self.log("Starred 2: {}".format(starred))

      starred = yield self.call(u'com.arguments.stars', stars = 5)
      self.log("Starred 3: {}".format(starred))

      starred = yield self.call(u'com.arguments.stars', nick = u'Homer', stars = 5)
      self.log("Starred 4: {}".format(starred))

      orders = yield self.call(u'com.arguments.orders', u'coffee')
      self.log("Orders 1: {}".format(orders))

      orders = yield self.call(u'com.arguments.orders', u'coffee', limit = 10)
      self.log("Orders 2: {}".format(orders))

      arglengths = yield self.call(u'com.arguments.arglen')
      self.log("Arglen 1: {}".format(arglengths))

      arglengths = yield self.call(u'com.arguments.arglen', 1, 2, 3)
      self.log("Arglen 1: {}".format(arglengths))

      arglengths = yield self.call(u'com.arguments.arglen', a = 1, b = 2, c = 3)
      self.log("Arglen 2: {}".format(arglengths))

      arglengths = yield self.call(u'com.arguments.arglen', 1, 2, 3, a = 1, b = 2, c = 3)
      self.log("Arglen 3: {}".format(arglengths))

      #self.leave()

      self.finish()


## test different deployment topologies
##

if __name__ == '__main__':

   import sys, argparse

   from twisted.python import log
   from twisted.internet.endpoints import serverFromString
   from twisted.internet.endpoints import clientFromString


   ## parse command line arguments
   ##
   parser = argparse.ArgumentParser()

   parser.add_argument("-d", "--debug", action = "store_true",
                       help = "Enable debug output.")

   parser.add_argument("-c", "--component", type = str, default = None,
                       help = "Start WAMP server with this application component, e.g. 'timeservice.TimeServiceBackend', or None.")

   parser.add_argument("-r", "--realm", type = str, default = "realm1",
                       help = "The WAMP realm to start the component in (if any).")

   parser.add_argument("-u", "--url", type = str, default = "ws://127.0.0.1:8080",
                       help = "WebSocket URL.")

   parser.add_argument("--server", type = str, default = "tcp:8080",
                       help = 'Twisted server endpoint descriptor, e.g. "tcp:8080" or "unix:/tmp/mywebsocket".')

   parser.add_argument("--client", type = str, default = "tcp:127.0.0.1:8080",
                       help = 'Twisted client endpoint descriptor, e.g. "tcp:127.0.0.1:8080" or "unix:/tmp/mywebsocket".')

   parser.add_argument("--transport", choices = ['websocket', 'rawsocket-json', 'rawsocket-msgpack'], default = "websocket",
                       help = 'WAMP transport type')

   args = parser.parse_args()


   ## start Twisted logging to stdout
   ##
   if args.debug:
      log.startLogging(sys.stdout)


   ## we use an Autobahn utility to install the "best" available Twisted reactor
   ##
   from autobahn.twisted.choosereactor import install_reactor
   reactor = install_reactor()
   if args.debug:
      print("Running on reactor {}".format(reactor))


   ## create a WAMP router factory
   ##
   from autobahn.wamp.router import RouterFactory
   router_factory = RouterFactory()


   ## create a WAMP router session factory
   ##
   from autobahn.twisted.wamp import RouterSessionFactory
   session_factory = RouterSessionFactory(router_factory)



   ## .. and create and add an WAMP application session to
   ## run next to the router
   ##
   from autobahn.wamp import types

   config = types.ComponentConfig(realm = args.realm,
      extra = {
         'caselog': 'case1.log'
      }
   )

   if False:
      embedded_components = [Case1_Backend]
      client_components = [Case1_Frontend]
   else:
      embedded_components = []
      #client_components = [Case2_Backend]
      #client_components = [Case1_Backend, Case1_Frontend]
      client_components = [Case2_Backend, Case2_Frontend]

   log = io.open(config.extra['caselog'], 'w')
   config.log = log
   config.components = []

   config.all_done = []

   for C in embedded_components:
      one_done = Deferred()
      config.all_done.append(one_done)
      c = C(config, one_done)
      config.components.append(c)
      session_factory.add(c)


   if args.transport == "websocket":

      ## create a WAMP-over-WebSocket transport server factory
      ##
      from autobahn.twisted.websocket import WampWebSocketServerFactory
      transport_factory = WampWebSocketServerFactory(session_factory, debug_wamp = args.debug)
      transport_factory.setProtocolOptions(failByDrop = False)

   elif args.transport in ['rawsocket-json', 'rawsocket-msgpack']:

      ## create a WAMP-over-RawSocket transport server factory
      ##
      if args.transport == 'rawsocket-msgpack':
         from autobahn.wamp.serializer import MsgPackSerializer
         serializer = MsgPackSerializer()
      elif args.transport == 'rawsocket-json':
         from autobahn.wamp.serializer import JsonSerializer
         serializer = JsonSerializer()
      else:
         raise Exception("should not arrive here")

      from autobahn.twisted.rawsocket import WampRawSocketServerFactory
      transport_factory = WampRawSocketServerFactory(session_factory, serializer, debug = args.debug)

   else:
      raise Exception("should not arrive here")


   from autobahn.twisted.websocket import WampWebSocketClientFactory, WampWebSocketClientProtocol

   ## start the server from an endpoint
   ##
   server = serverFromString(reactor, args.server)
   server.listen(transport_factory)

   clients = []
   clients_d = []
   for C in client_components:
      ## create a WAMP application session factory
      ##
      from autobahn.twisted.wamp import ApplicationSessionFactory
      session_factory = ApplicationSessionFactory(config)

      one_done = Deferred()
      config.all_done.append(one_done)

      def make_make(Klass, done):
         def make(config):
            c = Klass(config, done)
            config.components.append(c)
            return c
         return make

      ## .. and set the session class on the factory
      ##
      session_factory.session = make_make(C, one_done)

      if args.transport == "websocket":

         from autobahn.wamp.serializer import JsonSerializer

         serializers = [JsonSerializer()]

         ## create a WAMP-over-WebSocket transport client factory
         ##
         transport_factory = WampWebSocketClientFactory(session_factory, serializers = serializers, url = args.url, debug_wamp = args.debug)


         if False:
            def maker(Klass):
               class TestClientProtocol(WampWebSocketClientProtocol):
                  def onOpen(self):
                     self.txcnt = 0
                     self.rxcnt = 0
                     WampWebSocketClientProtocol.onOpen(self)

                  def sendMessage(self, bytes, isBinary):
                     self.txcnt += 1
                     print("> : {:>3} : {:<20} : {}".format(self.txcnt, Klass.__name__, bytes))
                     WampWebSocketClientProtocol.sendMessage(self, bytes, isBinary)

                  def onMessage(self, bytes, isBinary):
                     self.rxcnt += 1
                     print("< : {:>3} : {:<20} : {}".format(self.rxcnt, Klass.__name__, bytes))
                     WampWebSocketClientProtocol.onMessage(self, bytes, isBinary)
               return TestClientProtocol

            transport_factory.protocol = maker(C)
         else:
            transport_factory.protocol = WampWebSocketClientProtocol

         transport_factory.setProtocolOptions(failByDrop = False)

      elif args.transport in ['rawsocket-json', 'rawsocket-msgpack']:

         ## create a WAMP-over-RawSocket transport client factory
         ##
         if args.transport == 'rawsocket-msgpack':
            from autobahn.wamp.serializer import MsgPackSerializer
            serializer = MsgPackSerializer()
         elif args.transport == 'rawsocket-json':
            from autobahn.wamp.serializer import JsonSerializer
            serializer = JsonSerializer()
         else:
            raise Exception("should not arrive here")

         from autobahn.twisted.rawsocket import WampRawSocketClientFactory
         transport_factory = WampRawSocketClientFactory(session_factory, serializer, debug = args.debug)


      ## start the client from an endpoint
      ##
      cl = clientFromString(reactor, args.client)
      clients_d.append(cl.connect(transport_factory))

      clients.append(cl)


   d = DeferredList(config.all_done)
   #d = config.components[1]._done

   def done(res):
      log.flush()
      log.close()
      for c in config.components:
         c.leave()
      from twisted.internet import reactor
      reactor.callLater(1, reactor.stop)

   d.addCallback(done)

   ## now enter the Twisted reactor loop
   ##
   reactor.run()
