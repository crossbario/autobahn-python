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

class Case9_1_1(Case):

   DESCRIPTION = """Send text message message with payload of length 64 * 2**10 (64k)."""

   EXPECTATION = """Receive echo'ed text message (with payload as sent)."""

   def init(self):
      self.DATALEN = 64 * 2**10
      self.PAYLOAD = "BAsd7&jh23"
      self.WAITSECS = 10
      self.reportTime = True

   def onOpen(self):
      self.p.createWirelog = False
      self.behavior = Case.FAILED

      self.expectedClose = {"closedByMe":True,"closeCode":[self.p.CLOSE_STATUS_CODE_NORMAL],"requireClean":True}

      self.result = "Did not receive message within %d seconds." % self.WAITSECS
      self.p.sendFrame(opcode = 1, payload = self.PAYLOAD, payload_len = self.DATALEN)
      self.p.closeAfter(self.WAITSECS)

   def onMessage(self, msg, binary):
      if binary:
         self.result = "Expected text message with payload, but got binary."
      else:
         if len(msg) != self.DATALEN:
            self.result = "Expected text message with payload of length %d, but got %d." % (self.DATALEN, len(msg))
         else:
            ## FIXME : check actual content
            ##
            self.behavior = Case.OK
            self.result = "Received text message of length %d." % len(msg)
      self.p.createWirelog = True
      self.p.sendClose(self.p.CLOSE_STATUS_CODE_NORMAL)
