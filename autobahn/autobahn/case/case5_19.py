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

from case import Case

class Case5_19(Case):

   DESCRIPTION = """A fragmented text message is sent in multiple frames. After
   sending the first 2 frames of the text message, a Ping is sent. Then we wait 1s,
   then we send 2 more text fragments, another Ping and then the final text fragment.
   Everything is legal."""

   EXPECTATION = """The peer immediately answers the first Ping before
   it has received the last text message fragment. The peer pong's back the Ping's
   payload exactly, and echo's the payload of the fragmented message back to us."""


   def init(self):
      self.sync = False


   def onOpen(self):

      self.fragments = ["fragment1", "fragment2", "fragment3", "fragment4", "fragment5"]
      self.pings = ["pongme 1!", "pongme 2!"]

      self.expected[Case.OK] = [("pong", self.pings[0]), ("pong", self.pings[1]), ("message", ''.join(self.fragments), False)]
      self.expectedClose = {"closedByMe":True,"closeCode":[self.p.CLOSE_STATUS_CODE_NORMAL],"requireClean":True}

      self.p.sendFrame(opcode = 1, fin = False, payload = self.fragments[0], sync = self.sync)
      self.p.sendFrame(opcode = 0, fin = False, payload = self.fragments[1], sync = self.sync)
      self.p.sendFrame(opcode = 9, fin = True, payload = self.pings[0], sync = self.sync)
      self.p.continueLater(1, self.part2)


   def part2(self):

      self.p.sendFrame(opcode = 0, fin = False, payload = self.fragments[2], sync = self.sync)
      self.p.sendFrame(opcode = 0, fin = False, payload = self.fragments[3], sync = self.sync)
      self.p.sendFrame(opcode = 9, fin = True, payload = self.pings[1], sync = self.sync)
      self.p.sendFrame(opcode = 0, fin = True, payload = self.fragments[4], sync = self.sync)
      self.p.closeAfter(1)
