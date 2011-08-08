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

from case9_1_1 import *

class Case9_1_5(Case9_1_1):

   DESCRIPTION = """Send text message message with payload of length 8 * 2**20 (8M)."""

   EXPECTATION = """Receive echo'ed text message (with payload as sent)."""

   def init(self):
      self.DATALEN = 8 * 2**20
      self.PAYLOAD = "BAsd7&jh23"
      self.WAITSECS = 100
      self.reportTime = True
