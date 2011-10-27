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

class Case10_1_1(Case):

   DESCRIPTION = """Send text message with payload of length 65536 and <b>autoFragmentSize = 1300</b>."""

   EXPECTATION = """Receive echo'ed text message (with payload as sent and transmitted frame counts as expected). Clean close with normal code."""

   def onOpen(self):
      self.payload = "*" * 65536
      self.p.autoFragmentSize = 1300
      self.expected[Case.OK] = [("message", self.payload, False)]
      self.expectedClose = {"closedByMe": True, "closeCode": [self.p.CLOSE_STATUS_CODE_NORMAL], "requireClean": True}
      self.p.sendMessage(self.payload)
      self.p.killAfter(10)

   def onConnectionLost(self, failedByMe):
      Case.onConnectionLost(self, failedByMe)
      frames_expected = {}
      frames_expected[0] = len(self.payload) / self.p.autoFragmentSize
      frames_expected[1] = 1 if len(self.payload) % self.p.autoFragmentSize > 0 else 0
      frames_got = {}
      frames_got[0] = self.p.txFrameStats[0]
      frames_got[1] = self.p.txFrameStats[1]
      if frames_expected == frames_got:
         pass
      else:
         self.behavior = Case.FAILED
         self.result = "Frames transmitted %s does not match what we expected %s." % (str(frames_got), str(frames_expected))
