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

from cases import Case

class Case1(Case):

   DESCRIPTION = """A fragmented text message is sent in multiple frames. After
   sending the first 2 frames of the text message, a Ping is sent. Then we wait 1s,
   then we send 2 more text fragments, another Ping and then the final text fragment.
   Everything is legal."""

   EXPECTATION = """We test if the client immediately answers the first Ping before
   it has received the last text message fragment. Also we test if Ping payloads
   are Pong'ed back exactly, and if the fragmented message is echo'ed back to us."""

   def init(self):
      self.sync = False

   def onOpen(self):
      self.fragments = ["fragment1", "fragment2", "fragment3", "fragment4", "fragment5"]
      self.pings = ["pongme 1!", "pongme 2!"]
      self.received = []
      self.expected = [("pong", self.pings[0]), ("pong", self.pings[1]), ("message", ''.join(self.fragments))]
      self.step1()

   def step1(self):
      self.p.sendFrame(opcode = 1, fin = False, payload = self.fragments[0], sync = self.sync)
      self.p.sendFrame(opcode = 0, fin = False, payload = self.fragments[1], sync = self.sync)
      self.p.sendFrame(opcode = 9, fin = True, payload = self.pings[0], sync = self.sync)
      self.p.continueLater(1, self.step2)

   def step2(self):
      self.p.sendFrame(opcode = 0, fin = False, payload = self.fragments[2], sync = self.sync)
      self.p.sendFrame(opcode = 0, fin = False, payload = self.fragments[3], sync = self.sync)
      self.p.sendFrame(opcode = 9, fin = True, payload = self.pings[1], sync = self.sync)
      self.p.sendFrame(opcode = 0, fin = True, payload = self.fragments[4], sync = self.sync)
      self.p.continueLater(1, self.step3)

   def step3(self):
      self.passed = self.compare(self.received, self.expected)
      if not self.passed:
         self.result = "Expected %s, but got %s." % (str(self.expected), str(self.received))
      self.p.failConnection()

   def onPong(self, payload):
      self.received.append(("pong", payload))

   def onMessage(self, msg, binary):
      self.received.append(("message", msg))
