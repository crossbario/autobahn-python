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

from autobahn.util import newid, utcnow

from autobahn.httpstatus import HTTP_STATUS_CODE_BAD_REQUEST
from autobahn.websocket import HttpException
from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol
from autobahn.wamp import WampServerFactory, WampServerProtocol, exportRpc


URI_RPC = "http://wsperf.org/api#"
URI_EVENT = "http://wsperf.org/event#"


class WsPerfMasterProtocol(WebSocketServerProtocol):

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
      self.factory.removeSlave(self)
      self.slaveConnected = False
      self.slaveId = None

   def runCase(self, workerRunId, caseDef):
      test = {'uri': caseDef['uri'].encode('utf8'),
              'name': "foobar",
              'count': caseDef['count'],
              'quantile_count': caseDef['quantile_count'],
              'timeout': caseDef['timeout'],
              'binary': 'true' if caseDef['binary'] else 'false',
              'sync': 'true' if caseDef['sync'] else 'false',
              'rtts': 'true' if False else 'false',
              'correctness': str(caseDef['correctness']),
              'size': caseDef['size'],
              'token': workerRunId}

      cmd = self.WSPERF_CMD % test
      if self.factory.debugWsPerf:
         self.pp.pprint(cmd)
      self.sendMessage(cmd)
      return self.slaveId

   def protocolError(self, msg):
      self.sendClose(self, self.WSPERF_PROTOCOL_ERROR, msg)
      log.err("WSPERF_PROTOCOL_ERROR - %s" % msg)

   def onMessage(self, msg, binary):
      if not binary:
         if msg is not None:
            try:
               o = json.loads(msg)
               if self.factory.debugWsPerf:
                  self.pp.pprint(o)

               ## ERROR
               if o['type'] == u'error':
                  log.err("received ERROR")
                  self.pp.pprint(o)

               ## START
               elif o['type'] == u'test_start':
                  workerRunId = o['token']
                  workerId = o['data']['worker_id']
                  self.factory.caseStarted(workerRunId, workerId)

               ## DATA
               elif o['type'] == u'test_data':
                  workerRunId = o['token']
                  result = o['data']
                  self.factory.caseResult(workerRunId, result)

               ## COMPLETE
               elif o['type'] == u'test_complete':
                  workerRunId = o['token']
                  self.factory.caseCompleted(workerRunId)

               ## WELCOME
               elif o['type'] == u'test_welcome':
                  if self.slaveConnected:
                     self.protocolError("duplicate welcome message")
                  else:
                     self.slaveConnected = True
                     self.factory.addSlave(self, self.slaveId, self.peer.host, self.peer.port, o['version'], o['num_workers'], o['ident'])

            except ValueError, e:
               self.protocolError("could not decode text message as JSON (%s)" % str(e))
         else:
            self.protocolError("unexpected empty message")
      else:
         self.protocolError("unexpected binary message")


class WsPerfMasterFactory(WebSocketServerFactory):

   protocol = WsPerfMasterProtocol

   def startFactory(self):
      self.slavesToProtos = {}
      self.protoToSlaves = {}
      self.slaves = {}
      self.runs = {}
      self.workerRunsToRuns = {}

   def addSlave(self, proto, id, host, port, version, num_workers, ident):
      if not self.protoToSlaves.has_key(proto):
         self.protoToSlaves[proto] = id
      else:
         raise Exception("logic error - duplicate proto in addSlave")
      if not self.slavesToProtos.has_key(id):
         self.slavesToProtos[id] = proto
      else:
         raise Exception("logic error - duplicate id in addSlave")
      self.slaves[id] = {'id': id, 'host': host, 'port': port, 'version': version, 'ident': ident, 'num_workers': num_workers}
      self.uiFactory.slaveConnected(id, host, port, version, num_workers, ident)

   def removeSlave(self, proto):
      if self.protoToSlaves.has_key(proto):
         id = self.protoToSlaves[proto]
         del self.protoToSlaves[proto]
         if self.slavesToProtos.has_key(id):
            del self.slavesToProtos[id]
         if self.slaves.has_key(id):
            del self.slaves[id]
         self.uiFactory.slaveDisconnected(id)

   def getSlaves(self):
      return self.slaves.values()

   def runCase(self, caseDef):
      """
      Start a new test run on all currently connected slaves.
      """
      runId = newid()
      self.runs[runId] = {}
      workerRunCount = 0
      for proto in self.protoToSlaves:
         workerRunId = newid()
         slaveId = proto.runCase(workerRunId, caseDef)
         self.runs[runId][workerRunId] = {'slaveId': slaveId,
                                          'results': []}
         self.workerRunsToRuns[workerRunId] = runId
      return runId

   def caseStarted(self, workerRunId, workerId):
      runId = self.workerRunsToRuns[workerRunId]
      run = self.runs[runId][workerRunId]
      run['workerId'] = workerId

   def caseResult(self, workerRunId, result):
      runId = self.workerRunsToRuns[workerRunId]
      run = self.runs[runId][workerRunId]
      run['results'].append(result)
      self.uiFactory.caseResult(runId,
                                run['slaveId'],
                                run['workerId'],
                                result)

   def caseCompleted(self, workerRunId):
      runId = self.workerRunsToRuns[workerRunId]
      #del self.workerRunsToRuns[workerRunId]
      #del self.runs[runId]


class WsPerfMasterUiProtocol(WampServerProtocol):

   @exportRpc
   def runCase(self, caseDef):
      return self.factory.runCase(caseDef)

   @exportRpc
   def getSlaves(self):
      return self.factory.getSlaves()

   def onSessionOpen(self):
      self.registerForRpc(self, URI_RPC)
      self.registerForPubSub(URI_EVENT, True)


class WsPerfMasterUiFactory(WampServerFactory):

   protocol = WsPerfMasterUiProtocol

   def slaveConnected(self, id, host, port, version, num_workers, ident):
      self._dispatchEvent(URI_EVENT + "slaveConnected", {'id': id,
                                                         'host': host,
                                                         'port': port,
                                                         'version': version,
                                                         'num_workers': num_workers,
                                                         'ident': ident})

   def slaveDisconnected(self, id):
      self._dispatchEvent(URI_EVENT + "slaveDisconnected", {'id': id})

   def getSlaves(self):
      return self.slaveFactory.getSlaves()

   def runCase(self, caseDef):
      return self.slaveFactory.runCase(caseDef)

   def caseResult(self, runId, slaveId, workerId, result):
      event = {'runId': runId,
               'slaveId': slaveId,
               'workerId': workerId,
               'result': result}
      self._dispatchEvent(URI_EVENT + "caseResult", event)
