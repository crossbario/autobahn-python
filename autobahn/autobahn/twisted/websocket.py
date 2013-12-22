###############################################################################
##
##  Copyright 2011-2013 Tavendo GmbH
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

import twisted.internet.protocol
from twisted.internet.defer import maybeDeferred
from twisted.python import log

from autobahn.websocket import protocol



class WebSocketServerProtocol(protocol.WebSocketServerProtocol, twisted.internet.protocol.Protocol):
   """
   """

   def connectionMade(self):
      ## the peer we are connected to
      peer = self.transport.getPeer()
      try:
         self.peer = "%s:%d" % (peer.host, peer.port)
      except:
         ## eg Unix Domain sockets don't have host/port
         self.peer = str(peer)

      protocol.WebSocketServerProtocol.connectionMade(self)

      ## Set "Nagle"
      try:
         self.transport.setTcpNoDelay(self.tcpNoDelay)
      except:
         ## eg Unix Domain sockets throw Errno 22 on this
         pass


   #    peername = str(self.transport.getPeer())
   #    print('connection from {}'.format(peername))

   # def dataReceived(self, data):
   #    self._onData(data)
   #    #print('data received: {}'.format(data.decode()))
   #    #self.transport.write(data)
   #    #self.transport.loseConnection()

   # def connectionLost(self, reason):
   #    pass

   def _closeConnection(self, abort = False):
      if abort:
         self.transport.abortConnection()
      else:
         self.transport.loseConnection()


   def _run_onConnect(self, connectionRequest):

      ## onConnect() will return the selected subprotocol or None
      ## or a pair (protocol, headers) or raise an HttpException
      ##
      res = maybeDeferred(self.onConnect, connectionRequest)
      res.addCallback(self._processHandshake_buildResponse)
      res.addErrback(self._processHandshake_failed)


   def registerProducer(self, producer, streaming):
      """
      Register a Twisted producer with this protocol.

      Modes: Hybi, Hixie

      :param producer: A Twisted push or pull producer.
      :type producer: object
      :param streaming: Producer type.
      :type streaming: bool
      """
      self.transport.registerProducer(producer, streaming)




class WebSocketServerFactory(protocol.WebSocketServerFactory, twisted.internet.protocol.ServerFactory):
   """
   """

   def __init__(self, *args, **kwargs):

      #twisted.internet.protocol.ServerFactory.__init__(self)

      protocol.WebSocketServerFactory.__init__(self, *args, **kwargs)

      ## lazy import to avoid reactor install upon module import
      if 'reactor' in kwargs:
         self.reactor = kwargs['reactor']
      else:
         from twisted.internet import reactor
         self.reactor = reactor


   def _log(self, msg):
      log.msg(msg)


   def _callLater(self, delay, fun):
      return self.reactor.callLater(delay, fun)


   #protocol = WebSocketServerProtocol

   # def __init__(self, reactor = None):

   #    ## lazy import to avoid reactor install upon module import
   #    if reactor is None:
   #       from twisted.internet import reactor
   #    self._reactor = reactor


   # def buildProtocol(self, addr):
   #    proto = self.protocol()
   #    proto.factory = self
   #    return proto


class WebSocketClientProtocol(protocol.WebSocketClientProtocol, twisted.internet.protocol.Protocol):
   """
   """

   def connectionMade(self):
      ## the peer we are connected to
      peer = self.transport.getPeer()
      try:
         self.peer = "%s:%d" % (peer.host, peer.port)
      except:
         ## eg Unix Domain sockets don't have host/port
         self.peer = str(peer)

      protocol.WebSocketClientProtocol.connectionMade(self)

      ## Set "Nagle"
      try:
         self.transport.setTcpNoDelay(self.tcpNoDelay)
      except:
         ## eg Unix Domain sockets throw Errno 22 on this
         pass



   def registerProducer(self, producer, streaming):
      """
      Register a Twisted producer with this protocol.

      Modes: Hybi, Hixie

      :param producer: A Twisted push or pull producer.
      :type producer: object
      :param streaming: Producer type.
      :type streaming: bool
      """
      self.transport.registerProducer(producer, streaming)


   def _closeConnection(self, abort = False):
      if abort:
         self.transport.abortConnection()
      else:
         self.transport.loseConnection()



class WebSocketClientFactory(protocol.WebSocketClientFactory, twisted.internet.protocol.ClientFactory):
   """
   """

   def __init__(self, *args, **kwargs):

      #twisted.internet.protocol.ClientFactory.__init__(self)

      protocol.WebSocketClientFactory.__init__(self, *args, **kwargs)

      ## lazy import to avoid reactor install upon module import
      if 'reactor' in kwargs:
         self.reactor = kwargs['reactor']
      else:
         from twisted.internet import reactor
         self.reactor = reactor


   def _log(self, msg):
      log.msg(msg)


   def _callLater(self, delay, fun):
      return self.reactor.callLater(delay, fun)



def connectWS(factory, contextFactory = None, timeout = 30, bindAddress = None):
   """
   Establish WebSocket connection to a server. The connection parameters like target
   host, port, resource and others are provided via the factory.

   :param factory: The WebSocket protocol factory to be used for creating client protocol instances.
   :type factory: An :class:`autobahn.websocket.WebSocketClientFactory` instance.
   :param contextFactory: SSL context factory, required for secure WebSocket connections ("wss").
   :type contextFactory: A `twisted.internet.ssl.ClientContextFactory <http://twistedmatrix.com/documents/current/api/twisted.internet.ssl.ClientContextFactory.html>`_ instance.
   :param timeout: Number of seconds to wait before assuming the connection has failed.
   :type timeout: int
   :param bindAddress: A (host, port) tuple of local address to bind to, or None.
   :type bindAddress: tuple

   :returns: obj -- An object which implements `twisted.interface.IConnector <http://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IConnector.html>`_.
   """
   ## lazy import to avoid reactor install upon module import
   if hasattr(factory, 'reactor'):
      reactor = factory.reactor
   else:
      from twisted.internet import reactor

   if factory.proxy is not None:
      if factory.isSecure:
         raise Exception("WSS over explicit proxies not implemented")
      else:
         conn = reactor.connectTCP(factory.proxy['host'], factory.proxy['port'], factory, timeout, bindAddress)
   else:
      if factory.isSecure:
         if contextFactory is None:
            # create default client SSL context factory when none given
            from twisted.internet import ssl
            contextFactory = ssl.ClientContextFactory()
         conn = reactor.connectSSL(factory.host, factory.port, factory, contextFactory, timeout, bindAddress)
      else:
         conn = reactor.connectTCP(factory.host, factory.port, factory, timeout, bindAddress)
   return conn



def listenWS(factory, contextFactory = None, backlog = 50, interface = ''):
   """
   Listen for incoming WebSocket connections from clients. The connection parameters like
   listening port and others are provided via the factory.

   :param factory: The WebSocket protocol factory to be used for creating server protocol instances.
   :type factory: An :class:`autobahn.websocket.WebSocketServerFactory` instance.
   :param contextFactory: SSL context factory, required for secure WebSocket connections ("wss").
   :type contextFactory: A twisted.internet.ssl.ContextFactory.
   :param backlog: Size of the listen queue.
   :type backlog: int
   :param interface: The interface (derived from hostname given) to bind to, defaults to '' (all).
   :type interface: str

   :returns: obj -- An object that implements `twisted.interface.IListeningPort <http://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IListeningPort.html>`_.
   """
   ## lazy import to avoid reactor install upon module import
   if hasattr(factory, 'reactor'):
      reactor = factory.reactor
   else:
      from twisted.internet import reactor

   if factory.isSecure:
      if contextFactory is None:
         raise Exception("Secure WebSocket listen requested, but no SSL context factory given")
      listener = reactor.listenSSL(factory.port, factory, contextFactory, backlog, interface)
   else:
      listener = reactor.listenTCP(factory.port, factory, backlog, interface)
   return listener
