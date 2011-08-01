###############################################################################
##
##  Copyright 2011 Tavendo GmbH
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

from twisted.internet import reactor
from twisted.python import log
from websocket import WebSocketService, WebSocketServiceConnection, HttpException
import json
import binascii

class FuzzingServiceConnection(WebSocketServiceConnection):

   def onConnect(self, host, path, params, origin, protocols):
      if self.debug:
         log.msg("connection received from %s for host %s, path %s, parms %s, origin %s, protocols %s" % (self.peerstr, host, path, str(params), origin, str(protocols)))
      return None


   def onOpen(self):
      self.cases = {"case001": self.case001,
                    "case002": self.case002,
                    "case003": self.case003,
                    "case004a": self.case004a,
                    "case004b": self.case004b,
                    "case005": self.case005,
                    "case006": self.case006,
                    "case007a": self.case007a,
                    "case007b": self.case007b,
                    "case007c": self.case007c,
                    "case008": self.case008,
                    "case009": self.case009,
                    "case100": self.case100,
                    "case101": self.case101,
                    "case101": self.case101,
                    "case102": self.case102
                    }
      self.case = None


   def onPong(self, payload):
      if self.debug:
         log.msg("PONG of length %d received from %s : %s" % (len(payload), self.peerstr, payload))

      if self.case == "case003_part2":
         self.case003_part2()


   def onMessage(self, msg, binary):

      if not binary:

         obj = json.loads(msg)

         ## send frame as specified
         ##
         if obj[0] == "sendframe":
            pl = obj[1].get("payload", "")
            self.sendFrame(opcode = obj[1]["opcode"],
                           payload = pl.encode("UTF-8"),
                           fin = obj[1].get("fin", True),
                           rsv = obj[1].get("rsv", 0),
                           mask = obj[1].get("mask", None),
                           payload_len = obj[1].get("payload_len", None),
                           chopsize = obj[1].get("chopsize", None),
                           sync = obj[1].get("sync", False))

         ## send multiple frames as specified
         ##
         elif obj[0] == "sendframes":
            frames = obj[1]
            for frame in frames:
               pl = frame.get("payload", "")
               self.sendFrame(opcode = frame["opcode"],
                              payload = pl.encode("UTF-8"),
                              fin = frame.get("fin", True),
                              rsv = frame.get("rsv", 0),
                              mask = frame.get("mask", None),
                              payload_len = frame.get("payload_len", None),
                              chopsize = frame.get("chopsize", None),
                              sync = frame.get("sync", False))

         ## send close
         ##
         elif obj[0] == "close":
            spec = obj[1]
            self.sendClose(spec.get("code", None), spec.get("reason", None))

         ## echo argument
         ##
         elif obj[0] == "echo":
            spec = obj[1]
            self.sendFrame(opcode = 1, payload = spec.get("payload", ""), payload_len = spec.get("payload_len", None))

         ## run test case
         ##
         else:
            case = obj[0]
            if self.cases.has_key(case):
               log.msg("Executing %s" % case)
               self.case = case
               self.cases[self.case]()
            else:
               raise Exception("fuzzing server received unknown command/test case %s" % case)
      else:
         raise Exception("fuzzing server received binary message")


   ## legal sequence of fragmented text message
   ##
   def case001(self):
      self.sendFrame(opcode = 1, fin = False, payload = "fragment1-")
      self.sendFrame(opcode = 0, fin = False, payload = "fragment2-")
      self.sendFrame(opcode = 0, fin = False, payload = "fragment3-")
      self.sendFrame(opcode = 0, fin = False, payload = "fragment4-")
      self.sendFrame(opcode = 0, fin = True, payload = "fragment5")
      self.case = None


   ## legal sequence of fragmented text message with intermittant
   ## ping control frames
   ##
   def case002(self):
      self.sendFrame(opcode = 1, fin = False, payload = "fragment1-")
      self.sendFrame(opcode = 9, fin = True, payload = "ping1"*10)
      self.sendFrame(opcode = 0, fin = False, payload = "fragment2-")
      self.sendFrame(opcode = 0, fin = False, payload = "fragment3-")
      self.sendFrame(opcode = 9, fin = True, payload = "ping2"*10)
      self.sendFrame(opcode = 9, fin = True, payload = "ping3"*10)
      self.sendFrame(opcode = 0, fin = False, payload = "fragment4-")
      self.sendFrame(opcode = 0, fin = True, payload = "fragment5")
      self.case = None


   ## same as case002, but wait for first PONG to proceed with test case
   ##
   def case003(self):
      self.sendFrame(opcode = 1, fin = False, payload = "fragment1-")
      self.sendFrame(opcode = 9, fin = True, payload = "ping1"*10)
      self.case = "case003_part2"

   def case003_part2(self):
      self.sendFrame(opcode = 0, fin = False, payload = "fragment2-")
      self.sendFrame(opcode = 0, fin = False, payload = "fragment3-")
      self.sendFrame(opcode = 9, fin = True, payload = "ping2"*10)
      self.sendFrame(opcode = 9, fin = True, payload = "ping3"*10)
      self.sendFrame(opcode = 0, fin = False, payload = "fragment4-")
      self.sendFrame(opcode = 0, fin = True, payload = "fragment5")
      self.case = None

   ## same as case002, but wait for first PONG to proceed with test case
   ##
   def case004a(self):
      self.sendFrame(opcode = 1, fin = False, payload = "fragment1-")
      self.case = None

   def case004b(self):
      self.sendFrame(opcode = 9, fin = True, payload = "ping1"*10)
      self.sendFrame(opcode = 0, fin = False, payload = "fragment2-")
      self.sendFrame(opcode = 0, fin = False, payload = "fragment3-")
      self.sendFrame(opcode = 9, fin = True, payload = "ping2"*10)
      self.sendFrame(opcode = 9, fin = True, payload = "ping3"*10)
      self.sendFrame(opcode = 0, fin = False, payload = "fragment4-")
      self.sendFrame(opcode = 0, fin = True, payload = "fragment5")
      self.case = None

   ## legal sequence of fragmented text message with intermittant ping
   ##
   def case005(self):
      self.sendFrame(opcode = 1, fin = False, payload = "fragment1-")
      self.sendFrame(opcode = 9, fin = True, payload = "ping")
      self.sendFrame(opcode = 0, fin = True, payload = "fragment2")
      self.case = None

   ## same as case005, but really send out each frame on wire
   ## (this is done by running Select() on the underlying reactor)
   ##
   def case006(self):
      self.sendFrame(opcode = 1, fin = False, payload = "fragment1-")
      reactor.doSelect(0)
      self.sendFrame(opcode = 9, fin = True, payload = "ping")
      reactor.doSelect(0)
      self.sendFrame(opcode = 0, fin = True, payload = "fragment2")
      reactor.doSelect(0)
      self.case = None

   ## same as case005, but as individual commands
   ##
   def case007a(self):
      self.sendFrame(opcode = 1, fin = False, payload = "fragment1-")
      self.case = None

   def case007b(self):
      self.sendFrame(opcode = 9, fin = True, payload = "ping")
      self.case = None

   def case007c(self):
      self.sendFrame(opcode = 0, fin = True, payload = "fragment2")
      self.case = None

   ## same as case005, but use raw bytes as input to rule out bugs in
   ## this code
   ##
   def case008(self):
      data = ["010a667261676d656e74312d", "890470696e67", "8009667261676d656e7432"]
      for d in data:
         self.transport.write(binascii.a2b_hex(d))

   def case009(self):
      self.sendFrame(opcode = 1, fin = False, payload = "fragment1-", chopsize = 1)
      self.sendFrame(opcode = 9, fin = True, payload = "ping", chopsize = 1)
      self.sendFrame(opcode = 0, fin = True, payload = "fragment2", chopsize = 1)
      self.case = None

   def case100(self):
      """
      Start conversation by sending 3 continuation frames with FIN = True, where
      there is nothing to continue. This is bogus (continuation frames outside fragmented
      message), and the client should immediately close the connection.
      """
      self.sendFrame(opcode = 0, fin = True, payload = "bogus1")
      self.sendFrame(opcode = 0, fin = True, payload = "bogus*2")
      self.sendFrame(opcode = 0, fin = True, payload = "bogus**3")
      self.sendFrame(opcode = 1, fin = True, payload = "BLUB!")
      self.case = None

   def case101(self):
      """
      Same as case101, but send out frames synchronously.
      """
      self.sendFrame(opcode = 0, fin = True, payload = "bogus1", sync = True)
      self.sendFrame(opcode = 0, fin = True, payload = "bogus*2", sync = True)
      self.sendFrame(opcode = 0, fin = True, payload = "bogus**3", sync = True)
      self.sendFrame(opcode = 1, fin = True, payload = "BLUB!", sync = True)
      self.case = None

   def case102(self):
      """
      Same as case102, but send out frames chooped into single octets.
      """
      self.sendFrame(opcode = 0, fin = True, payload = "bogus1", chopsize = 1)
      self.sendFrame(opcode = 0, fin = True, payload = "bogus*2", chopsize = 1)
      self.sendFrame(opcode = 0, fin = True, payload = "bogus**3", chopsize = 1)
      self.sendFrame(opcode = 1, fin = True, payload = "BLUB!", chopsize = 1)
      self.case = None


class FuzzingService(WebSocketService):

   protocol = FuzzingServiceConnection

   def __init__(self, debug = False):
      self.debug = debug

   def startFactory(self):
      pass

   def stopFactory(self):
      pass
