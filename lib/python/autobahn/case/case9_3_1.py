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

class Case9_3_1(Case):

   DESCRIPTION = """Send fragmented text message message with message payload of length 4 * 2**20 (4M). Sent out in fragments of 64."""

   EXPECTATION = """Receive echo'ed text message (with payload as sent)."""

   def init(self):
      self.DATALEN = 4 * 2**20
      self.FRAGSIZE = 64
      self.PAYLOAD = "*" * self.DATALEN
      self.WAITSECS = 100
      self.reportTime = True

   def onOpen(self):
      self.p.createWirelog = False
      self.behavior = Case.FAILED
      self.expectedClose = {"closedByMe":True,"closeCode":[self.p.CLOSE_STATUS_CODE_NORMAL],"requireClean":True}
      self.result = "Did not receive message within %d seconds." % self.WAITSECS
      self.p.sendMessage(payload = self.PAYLOAD, binary = False, payload_frag_size = self.FRAGSIZE)
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


