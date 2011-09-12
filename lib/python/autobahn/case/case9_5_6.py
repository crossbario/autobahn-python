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

from case9_5_1 import Case9_5_1

class Case9_5_6(Case9_5_1):

   DESCRIPTION = """Send text message message with payload of length 1 * 2**20 (1M). Sent out data in chops of 2048 octets."""

   EXPECTATION = """Receive echo'ed text message (with payload as sent)."""

   def setChopSize(self):
      self.chopsize = 2048
