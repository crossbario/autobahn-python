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

import sys, argparse

from twisted.python import log
from twisted.internet import reactor

import autobahn
from autobahn.websocket import listenWS
from autobahn.wamp import WampServerFactory, WampServerProtocol


class LoadLatencyBrokerProtocol(WampServerProtocol):

   def onSessionOpen(self):
      self.registerForPubSub(self.factory.config.topic)
      print "Load/Latency Broker client connected and brokering topic %s registered" % self.factory.config.topic


   def onClose(self, wasClean, code, reason):
      print "Load/Latency Broker client lost"


class LoadLatencyBrokerFactory(WampServerFactory):

   protocol = LoadLatencyBrokerProtocol

   def __init__(self, config):
      self.config = config
      WampServerFactory.__init__(self, config.wsuri, debugWamp = config.debug)

      self.setProtocolOptions(failByDrop = False)

      if config.skiputf8validate:
         self.setProtocolOptions(utf8validateIncoming = False)

      if config.allowunmasked:
         self.setProtocolOptions(requireMaskedClientFrames = False)

      print "Load/Latency Broker listening on %s [skiputf8validate = %s, allowunmasked = %s]" % (config.wsuri, config.skiputf8validate, config.allowunmasked)



if __name__ == '__main__':

   parser = argparse.ArgumentParser(prog = "llserver",
                                    description = "Load/Latency Test Broker")

   parser.add_argument("-d",
                       "--debug",
                       help = "Enable debug output.",
                       action = "store_true")

   parser.add_argument("--skiputf8validate",
                       help = "Skip UTF8 validation of incoming messages.",
                       action = "store_true")

   parser.add_argument("--allowunmasked",
                       help = "Allow unmasked client frames.",
                       action = "store_true")

   parser.add_argument("-w",
                       "--wsuri",
                       type = str,
                       default = "ws://localhost:9000",
                       help = "Listening URI of WAMP server, e.g. ws://localhost:9000.")

   parser.add_argument("-t",
                       "--topic",
                       type = str,
                       default = "http://example.com/simple",
                       help = "Topic URI to use, e.g. http://example.com/simple")

   config = parser.parse_args()

   if config.debug:
      log.startLogging(sys.stdout)

   factory = LoadLatencyBrokerFactory(config)
   listenWS(factory)

   print reactor.__class__
   print autobahn.utf8validator.Utf8Validator
   print autobahn.xormasker.XorMaskerNull
   print autobahn.wamp.json_lib
   reactor.run()
