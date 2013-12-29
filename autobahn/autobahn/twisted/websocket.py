###############################################################################
##
##  Copyright (C) 2011-2013 Tavendo GmbH
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

__all__ = ['WebSocketServerProtocol',
           'WebSocketServerFactory',
           'WebSocketClientProtocol',
           'WebSocketClientFactory',
           'listenWS',
           'connectWS']

import twisted.internet.protocol
from twisted.internet.defer import maybeDeferred
from twisted.python import log

from autobahn.websocket import protocol
from autobahn.websocket import http


class WebSocketAdapterProtocol(twisted.internet.protocol.Protocol):
   """
   Adapter class for Twisted WebSocket protocols.
   """

   def connectionMade(self):
      ## the peer we are connected to
      peer = self.transport.getPeer()
      try:
         self.peer = "%s:%d" % (peer.host, peer.port)
      except:
         ## eg Unix Domain sockets don't have host/port
         self.peer = str(peer)

      self._connectionMade()

      ## Set "Nagle"
      try:
         self.transport.setTcpNoDelay(self.tcpNoDelay)
      except:
         ## eg Unix Domain sockets throw Errno 22 on this
         pass


   def connectionLost(self, reason):
      self._connectionLost(reason)


   def dataReceived(self, data):
      self._dataReceived(data)


   def _closeConnection(self, abort = False):
      if abort:
         self.transport.abortConnection()
      else:
         self.transport.loseConnection()


   def _onOpen(self):
      self.onOpen()

   def _onMessageBegin(self, isBinary):
      self.onMessageBegin(isBinary)

   def _onMessageFrameBegin(self, length):
      self.onMessageFrameBegin(length)

   def _onMessageFrameData(self, payload):
      self.onMessageFrameData(payload)

   def _onMessageFrameEnd(self):
      self.onMessageFrameEnd()

   def _onMessageFrame(self, payload):
      self.onMessageFrame(payload)

   def _onMessageEnd(self):
      self.onMessageEnd()

   def _onMessage(self, payload, isBinary):
      self.onMessage(payload, isBinary)

   def _onPing(self, payload):
      self.onPing(payload)

   def _onPong(self, payload):
      self.onPong(payload)

   def _onClose(self, wasClean, code, reason):
      self.onClose(wasClean, code, reason)


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



class WebSocketServerProtocol(WebSocketAdapterProtocol, protocol.WebSocketServerProtocol):
   """
   Base class for Twisted WebSocket server protocols.
   """

   def _onConnect(self, request):
      ## onConnect() will return the selected subprotocol or None
      ## or a pair (protocol, headers) or raise an HttpException
      ##
      res = maybeDeferred(self.onConnect, request)

      res.addCallback(self.succeedHandshake)

      def forwardError(failure):
         if failure.check(http.HttpException):
            return self.failHandshake(failure.value.reason, failure.value.code)
         else:
            if self.debug:
               self.factory._log("Unexpected exception in onConnect ['%s']" % failure.value)
            return self.failHandshake(http.INTERNAL_SERVER_ERROR[1], http.INTERNAL_SERVER_ERROR[0])

      res.addErrback(forwardError)



class WebSocketClientProtocol(WebSocketAdapterProtocol, protocol.WebSocketClientProtocol):
   """
   Base class for Twisted WebSocket client protocols.
   """

   def _onConnect(self, response):
      self.onConnect(response)



class WebSocketAdapterFactory:
   """
   Adapter class for Twisted WebSocket factories.
   """

   def _log(self, msg):
      log.msg(msg)


   def _callLater(self, delay, fun):
      return self.reactor.callLater(delay, fun)



class WebSocketServerFactory(WebSocketAdapterFactory, protocol.WebSocketServerFactory, twisted.internet.protocol.ServerFactory):
   """
   Base class for Twisted WebSocket server factories.
   """

   def __init__(self, *args, **kwargs):

      protocol.WebSocketServerFactory.__init__(self, *args, **kwargs)

      ## lazy import to avoid reactor install upon module import
      if 'reactor' in kwargs:
         self.reactor = kwargs['reactor']
      else:
         from twisted.internet import reactor
         self.reactor = reactor


   def startFactory(self):
      """
      Called by Twisted before starting to listen on port for incoming connections.
      Default implementation does nothing. Override in derived class when appropriate.
      """
      pass


   def stopFactory(self):
      """
      Called by Twisted before stopping to listen on port for incoming connections.
      Default implementation does nothing. Override in derived class when appropriate.
      """
      pass



class WebSocketClientFactory(WebSocketAdapterFactory, protocol.WebSocketClientFactory, twisted.internet.protocol.ClientFactory):
   """
   Base class for Twisted WebSocket client factories.
   """

   def __init__(self, *args, **kwargs):

      protocol.WebSocketClientFactory.__init__(self, *args, **kwargs)

      ## lazy import to avoid reactor install upon module import
      if 'reactor' in kwargs:
         self.reactor = kwargs['reactor']
      else:
         from twisted.internet import reactor
         self.reactor = reactor


   def clientConnectionFailed(self, connector, reason):
      """
      Called by Twisted when the connection to server has failed. Default implementation
      does nothing. Override in derived class when appropriate.
      """
      pass


   def clientConnectionLost(self, connector, reason):
      """
      Called by Twisted when the connection to server was lost. Default implementation
      does nothing. Override in derived class when appropriate.
      """
      pass



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
