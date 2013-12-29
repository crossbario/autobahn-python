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

import sys

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
                                       WebSocketServerProtocol, \
                                       listenWS

from autobahn.websocket.http import HttpException



class BaseService:
   """
   Simple base for our services.
   """
   def __init__(self, proto):
      self.proto = proto

   def onOpen(self):
      pass

   def onClose(self, wasClean, code, reason):
      pass

   def onMessage(self, payload, isBinary):
      pass


class Echo1Service(BaseService):
   """
   Awesome Echo Service 1.
   """
   def onMessage(self, payload, isBinary):
      if not isBinary:
         msg = "Echo 1 - {}".format(payload.decode('utf8'))
         self.proto.sendMessage(msg.encode('utf8'))



class Echo2Service(BaseService):
   """
   Awesome Echo Service 2.
   """
   def onMessage(self, payload, isBinary):
      if not isBinary:
         msg = "Echo 2 - {}".format(payload.decode('utf8'))
         self.proto.sendMessage(msg.encode('utf8'))



class ServiceServerProtocol(WebSocketServerProtocol):

   SERVICEMAP = {'/echo1': Echo1Service,
                 '/echo2': Echo2Service}

   def __init__(self):
      self.service = None

   def onConnect(self, request):
      ## request has all the information from the initial
      ## WebSocket opening handshake ..
      print(request.peer)
      print(request.headers)
      print(request.host)
      print(request.path)
      print(request.params)
      print(request.version)
      print(request.origin)
      print(request.protocols)
      print(request.extensions)

      ## We map to services based on path component of the URL the
      ## WebSocket client requested. This is just an example. We could
      ## use other information from request, such has HTTP headers,
      ## WebSocket subprotocol, WebSocket origin etc etc
      ##
      if self.SERVICEMAP.has_key(request.path):
         self.service = self.SERVICEMAP[request.path](self)
      else:
         err = "No service under %s" % request.path
         print(err)
         raise HttpException(404, err)

   def onOpen(self):
      if self.service:
         self.service.onOpen()

   def onMessage(self, payload, isBinary):
      if self.service:
         self.service.onMessage(payload, isBinary)

   def onClose(self, wasClean, code, reason):
      if self.service:
         self.service.onClose(wasClean, code, reason)



if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   factory = WebSocketServerFactory("ws://localhost:9000",
                                    debug = debug,
                                    debugCodePaths = debug)

   factory.protocol = ServiceServerProtocol
   factory.setProtocolOptions(allowHixie76 = True, failByDrop = False)
   listenWS(factory)

   webdir = File(".")
   web = Site(webdir)
   reactor.listenTCP(8080, web)

   reactor.run()
