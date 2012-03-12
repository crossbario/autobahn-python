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

from case5_19 import *

class Case5_20(Case5_19):

   DESCRIPTION = """Same as Case 5.19, but send all frames with SYNC = True.
   Note, this does not change the octets sent in any way, only how the stream
   is chopped up on the wire."""

   EXPECTATION = """Same as Case 5.19. Implementations must be agnostic to how
   octet stream is chopped up on wire (must be TCP clean)."""

   def init(self):
      self.sync = True
