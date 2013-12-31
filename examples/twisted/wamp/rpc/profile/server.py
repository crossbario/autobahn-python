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

import sys, math, time

from twisted.python import log
from twisted.internet import reactor, defer, threads


from autobahn.twisted.websocket import listenWS
from autobahn.wamp import exportRpc, \
                          WampServerFactory, \
                          WampServerProtocol


RPC_SUCCESS_TIMINGS = [('RECV', 'onMessageBegin', 'onBeforeCall'),
                       ('CALL', 'onBeforeCall', 'onAfterCallSuccess'),
                       ('SEND', 'onAfterCallSuccess', 'onAfterSendCallSuccess')]

RPC_ERROR_TIMINGS = [('RECV', 'onMessageBegin', 'onBeforeCall'),
                     ('CALL', 'onBeforeCall', 'onAfterCallError'),
                     ('SEND', 'onAfterCallError', 'onAfterSendCallError')]


class SimpleServerProtocol(WampServerProtocol):
   """

   onMessageBegin
   onMessage
   onBeforeCall
   onAfterCallSuccess / onAfterCallError
   sendMessage
   onAfterSendCallSuccess / onAfterSendCallError
   """

   def onSessionOpen(self):
      print "\nNew session:", self.session_id
      self.registerForRpc(self, "http://example.com/simple/calc#")

   def onClose(self, wasClean, code, reason):
      print "\nSession closed."

   def printTimings(self, callid, timings, tdef):
      sys.stdout.write(" %s | " % callid)
      for t in tdef:
         sys.stdout.write(t[0])
         sys.stdout.write(": ")
         sys.stdout.write(timings[2].diff(t[1], t[2]))
         sys.stdout.write(" | ")
      sys.stdout.write("%s" % timings[0])
      print

   def onAfterSendCallSuccess(self, _, callid):
      self.printTimings(callid, self.trackedRpcs[callid], RPC_SUCCESS_TIMINGS)

   def onAfterSendCallError(self, _, callid):
      self.printTimings(callid, self.trackedRpcs[callid], RPC_ERROR_TIMINGS)

   @exportRpc
   def println(self, msg):
      print msg

   @exportRpc
   def sum(self, list):
      return reduce(lambda x, y: x + y, list)

   @exportRpc("tsum")
   def threadSum(self, list):
      return threads.deferToThread(self.sum, list)

   @exportRpc("asum")
   def asyncSum(self, list, delay):
      ## Simulate a slow function.
      d = defer.Deferred()
      reactor.callLater(delay, d.callback, self.sum(list))
      return d

   @exportRpc("wsum")
   def workerSum(self, list, delay):
      ## Execute a slow function on thread from background thread pool.
      def wsum(list):
         if delay > 0:
            time.sleep(delay)
         return self.sum(list)
      return threads.deferToThread(wsum, list)


if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   factory = WampServerFactory("ws://localhost:9000", debugWamp = debug)
   factory.protocol = SimpleServerProtocol
   factory.setProtocolOptions(allowHixie76 = True)
   factory.trackTimings = True
   listenWS(factory)

   poolSize = 5
   print "Thread pool size:", poolSize

   reactor.suggestThreadPoolSize(poolSize)
   reactor.run()
