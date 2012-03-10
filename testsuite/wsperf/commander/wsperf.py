###############################################################################
##
##  Copyright 2012 Tavendo GmbH
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

import sys, json, pprint

from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import WebSocketServerFactory, \
                               WebSocketServerProtocol, \
                               listenWS

from autobahn.wamp import exportRpc, \
                          WampServerFactory, \
                          WampServerProtocol

from autobahn.util import newid, utcnow

from autobahn.websocket import HttpException
from autobahn.httpstatus import HTTP_STATUS_CODE_BAD_REQUEST

URI_RPC = "http://wsperf.org/api#"
URI_EVENT = "http://wsperf.org/event#"


class WsPerfProtocol(WebSocketServerProtocol):

   WSPERF_PROTOCOL_ERROR = 3000
   WSPERF_CMD = """message_test:uri=%(uri)s;token=%(token)s;size=%(size)d;count=%(count)d;quantile_count=%(quantile_count)d;timeout=%(timeout)d;binary=%(binary)s;sync=%(sync)s;rtts=%(rtts)s;correctness=%(correctness)s;"""

   def toMicroSec(self, value):
      return ("%." + str(self.factory.digits) + "f") % round(float(value), self.factory.digits)

   def getMicroSec(self, result, field):
      return self.toMicroSec(result['data'][field])

   def onConnect(self, connectionRequest):
      if 'wsperf' in connectionRequest.protocols:
         return 'wsperf'
      else:
         raise HttpException(httpstatus.HTTP_STATUS_CODE_BAD_REQUEST[0],
                             "You need to speak wsperf subprotocol with this server!")

   def onOpen(self):
      self.pp = pprint.PrettyPrinter(indent = 3)
      self.slaveConnected = False
      self.slaveId = newid()

   def onClose(self, wasClean, code, reason):
      self.factory.removeSlave(self.slaveId)
      self.factory.uiFactory.slaveDisconnected(self.slaveId)
      self.slaveConnected = False
      self.slaveId = None

   def runCase(self, caseDef):
      id = newid()
      test = {'uri': "ws://localhost:9000",
              'name': "foobar",
              'count': 100,
              'quantile_count': 10,
              'timeout': 10000,
              'binary': 'true' if True else 'false',
              'sync': 'true' if True else 'false',
              'rtts': 'true' if False else 'false',
              'correctness': 'exact' if False else 'length',
              'size': 4096,
              'token': id}
      cmd = self.WSPERF_CMD % test
      print cmd
      self.sendMessage(cmd)

   def protocolError(self, msg):
      self.sendClose(self, self.WSPERF_PROTOCOL_ERROR, msg)
      log.err("WSPERF_PROTOCOL_ERROR - %s" % msg)

   def onMessage(self, msg, binary):
      if not binary:
         try:
            o = json.loads(msg)
            if self.factory.debugWsPerf:
               self.pp.pprint(o)

            if o['type'] == u'error':
               pass
            elif o['type'] == u'test_complete':
               pass
            elif o['type'] == u'test_data':
               self.factory.uiFactory.caseResult(o)

            ## WELCOME
            ##
            ## {"type":"test_welcome","version":"wsperf/0.2.0dev WebSocket++/0.2.0dev","ident":"win1"}
            ##
            elif o['type'] == u'test_welcome':
               if self.slaveConnected:
                  self.protocolError("duplicate welcome message")
               else:
                  self.slaveConnected = True
                  self.factory.addSlave(self, self.slaveId)
                  self.factory.uiFactory.slaveConnected(self.slaveId, self.peer.host, self.peer.port, o['version'], o['ident'])
         except ValueError, e:
            raise Exception("could not decode text message as JSON (%s)" % str(e))
      else:
         raise Exception("unexpected binary message")


class WsPerfFactory(WebSocketServerFactory):

   protocol = WsPerfProtocol

   def startFactory(self):
      self.slavesToProtos = {}
      self.protoToSlaves = {}

   def addSlave(self, proto, id):
      if not self.protoToSlaves.has_key(proto):
         self.protoToSlaves[proto] = id
      else:
         raise Exception("logic error - duplicate proto in addSlave")
      if not self.slavesToProtos.has_key(id):
         self.slavesToProtos[id] = proto
      else:
         raise Exception("logic error - duplicate id in addSlave")

   def removeSlave(self, proto):
      if self.protoToSlaves.has_key(proto):
         id = self.protoToSlaves[proto]
         del self.protoToSlaves[proto]
         if self.slavesToProtos.has_key(id):
            del self.slavesToProtos[id]

   def runCase(self, caseDef):
      for proto in self.protoToSlaves:
         print "runCase", proto
         proto.runCase(caseDef)



class WsPerfUiProtocol(WampServerProtocol):

   @exportRpc
   def sum(self, list):
      return reduce(lambda x, y: x + y, list)

   @exportRpc
   def runCase(self, caseDef):
      print "runCase", caseDef
      self.factory.slaveFactory.runCase(caseDef)

   def onSessionOpen(self):
      self.registerForRpc(self, URI_RPC)
      self.registerForPubSub(URI_EVENT, True)
      #reactor.callLater(1, self.slaveConnected)


class WsPerfUiFactory(WampServerFactory):

   protocol = WsPerfUiProtocol

   def slaveConnected(self, id, host, port, version, ident):
      self._dispatchEvent(URI_EVENT + "slaveConnected", {'id': id,
                                                         'host': host,
                                                         'port': port,
                                                         'version': version,
                                                         'ident': ident})

   def slaveDisconnected(self, id):
      self._dispatchEvent(URI_EVENT + "slaveDisconnected", {'id': id})

   def caseResult(self, result):
      self._dispatchEvent(URI_EVENT + "caseResult", result)



if __name__ == '__main__':

   log.startLogging(sys.stdout)

   ## WAMP Server for wsperf slaves
   ##
   wsperf = WsPerfFactory("ws://localhost:9090")
   #wsperf.debug = True
   wsperf.debugWsPerf = True
   listenWS(wsperf)

   ## Web Server for UI static files
   ##
   webdir = File("static")
   web = Site(webdir)
   reactor.listenTCP(8080, web)

   ## WAMP Server for UI
   ##
   wsperfUi = WsPerfUiFactory("ws://localhost:9091")
   listenWS(wsperfUi)

   ## Connect servers
   ##
   wsperf.uiFactory = wsperfUi
   wsperfUi.slaveFactory = wsperf

   ## Run everything ..
   ##
   reactor.run()
