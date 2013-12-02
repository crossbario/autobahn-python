###############################################################################
##
##  Copyright 2013 Tavendo GmbH
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

import time, sys, argparse

from twisted.python import log
from twisted.internet import reactor

from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampCraClientProtocol



class LoadLatencySubscriberProtocol(WampCraClientProtocol):

   def onSessionOpen(self):

      if self.factory.config.debug:
         print "Load/Latency Subscriber Client connected to %s [skiputf8validate = %s, skipmasking = %s]" % (self.factory.config.wsuri, self.factory.config.skiputf8validate, self.factory.config.skipmasking)

      ## "authenticate" as anonymous
      d = self.authenticate()
      d.addCallbacks(self.onAuthSuccess, self.onAuthError)


   def onAuthSuccess(self, permissions):
      print "Authenticated."

      def onEvent(topic, event):
         rtt = time.clock() - event['sent']
         self.factory.receivedRtts.append(rtt)
         self.factory.receivedCnt += 1

      self.subscribe(self.factory.config.topic, onEvent)


   def onAuthError(self, e):
      uri, desc, details = e.value.args
      print "Authentication Error!", uri, desc, details



class LoadLatencySubscriberFactory(WampClientFactory):

   protocol = LoadLatencySubscriberProtocol

   def __init__(self, config):

      WampClientFactory.__init__(self, config.wsuri, debugWamp = config.debug)

      self.config = config
      self.receivedCnt = 0
      self.receivedRtts = []

      self.setProtocolOptions(failByDrop = False)

      if config.skiputf8validate:
         self.setProtocolOptions(utf8validateIncoming = False)

      if config.skipmasking:
         self.setProtocolOptions(maskClientFrames = False)



class LoadLatencyPublisherProtocol(WampCraClientProtocol):

   def onSessionOpen(self):

      if self.factory.config.debug:
         print "Load/Latency Publisher Client connected to %s [skiputf8validate = %s, skipmasking = %s]" % (self.factory.config.wsuri, self.factory.config.skiputf8validate, self.factory.config.skipmasking)

      ## "authenticate" as anonymous
      d = self.authenticate()
      d.addCallbacks(self.onAuthSuccess, self.onAuthError)


   def onAuthSuccess(self, permissions):
      print "Authenticated."

      def sendEvent():

         self.factory.batchid += 1
         msg = {'msg': '*' * self.factory.config.payload}
         for i in xrange(self.factory.config.batch):
            self.factory.id += 1
            self.factory.publishedCnt += 1
            #msg['id'] = self.factory.id
            #msg['batchid'] = self.factory.batchid
            msg['sent'] = time.clock()
            self.publish(self.factory.config.topic, msg)

         reactor.callLater(1. / float(self.factory.config.rate), sendEvent)

      sendEvent()


   def onAuthError(self, e):
      uri, desc, details = e.value.args
      print "Authentication Error!", uri, desc, details



class LoadLatencyPublisherFactory(WampClientFactory):

   protocol = LoadLatencyPublisherProtocol

   def __init__(self, config):

      WampClientFactory.__init__(self, config.wsuri, debugWamp = config.debug)

      self.config = config
      self.id = 0
      self.batchid = 0
      self.publishedCnt = 0

      self.setProtocolOptions(failByDrop = False)

      if config.skiputf8validate:
         self.setProtocolOptions(utf8validateIncoming = False)

      if config.skipmasking:
         self.setProtocolOptions(maskClientFrames = False)



class LoadLatencyTest:

   def __init__(self, config):
      self.config = config
      self.publishedCntTotal = 0
      self.receivedCntTotal = 0

   def run(self):
      self._factories = []
      for i in xrange(self.config.clients):
         factory = LoadLatencySubscriberFactory(self.config)
         connectWS(factory)
         self._factories.append(factory)

      publisherFactory = LoadLatencyPublisherFactory(self.config)
      connectWS(publisherFactory)

      def printstats():
         publishedCnt = publisherFactory.publishedCnt
         receivedCnt = sum([x.receivedCnt for x in self._factories])
         receivedSumRtts = 1000. * sum([sum(x.receivedRtts) for x in self._factories])

         if receivedCnt:
            rttAvg = float(receivedSumRtts) / float(receivedCnt)
         else:
            rttAvg = 0

         publisherFactory.publishedCnt = 0
         for f in self._factories:
            f.receivedCnt = 0
            f.receivedRtts = []

         self.publishedCntTotal += publishedCnt
         self.receivedCntTotal += receivedCnt

         print "%d, %d, %d, %d, %f" % (publishedCnt, receivedCnt, self.publishedCntTotal, self.receivedCntTotal, rttAvg)

         reactor.callLater(1, printstats)

      print "Messages:"
      print "sent_last, recv_last, sent_total, recv_total, rtt"
      printstats()



if __name__ == '__main__':

   parser = argparse.ArgumentParser(prog = "llclient",
                                    description = "Load/Latency Test Client")

   parser.add_argument("-d",
                       "--debug",
                       help = "Enable debug output.",
                       action = "store_true")

   parser.add_argument("--skiputf8validate",
                       help = "Skip UTF8 validation of incoming messages.",
                       action = "store_true")

   parser.add_argument("--skipmasking",
                       help = "Skip masking of sent frames.",
                       action = "store_true")

   parser.add_argument("-c",
                       "--clients",
                       type = int,
                       default = 10,
                       help = "Number of WAMP clients to connect.")

   parser.add_argument("-p",
                       "--payload",
                       type = int,
                       default = 10,
                       help = "Length of string field payload in bytes of each published message.")

   parser.add_argument("-b",
                       "--batch",
                       type = int,
                       default = 1,
                       help = "Number of messages published per batch.")

   parser.add_argument("-r",
                       "--rate",
                       type = int,
                       default = 25,
                       help = "Number of batches per second.")

   parser.add_argument("-w",
                       "--wsuri",
                       type = str,
                       default = "ws://127.0.0.1:9000",
                       help = "URI of WAMP server, e.g. ws://127.0.0.1:9000.")

   parser.add_argument("-t",
                       "--topic",
                       type = str,
                       default = "http://example.com/simple",
                       help = "Topic URI to use, e.g. http://example.com/simple")

   config = parser.parse_args()

   if config.debug:
      log.startLogging(sys.stdout)

   test = LoadLatencyTest(config)
   test.run()

   reactor.run()
