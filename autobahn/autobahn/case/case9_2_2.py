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

from case9_2_1 import *

class Case9_2_2(Case9_2_1):

   DESCRIPTION = """Send binary message message with payload of length 256 * 2**10 (256k)."""

   EXPECTATION = """Receive echo'ed binary message (with payload as sent)."""

   def init(self):
      self.DATALEN = 256 * 2**10
      self.PAYLOAD = "\x00\xfe\x23\xfa\xf0"
      self.WAITSECS = 10
      self.reportTime = True
