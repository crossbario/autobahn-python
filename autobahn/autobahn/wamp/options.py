###############################################################################
##
##  Copyright (C) 2013-2014 Tavendo GmbH
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

from __future__ import absolute_import


class Publish:
   """
   Wrapper allowing to specify a topic to be published to while providing
   details on exactly how the publishing should be performed.
   """

   def __init__(self,
                excludeMe = None,
                exclude = None,
                eligible = None,
                discloseMe = None):
      """
      Constructor.
      
      :param topic: The URI of the topic to publish to, e.g. "com.myapp.mytopic1".
      :type topic: str
      :param discloseMe: Request to disclose the identity of the caller (it's WAMP session ID)
                         to Callees. Note that a Dealer, depending on Dealer configuration, might
                         reject the request, or might disclose the Callee's identity without
                         a request to do so.
      :type discloseMe: bool
      """
      assert(excludeMe is None or type(excludeMe) == bool)
      assert(exclude is None or (type(exclude) == list and all(type(x) == int for x in exclude)))
      assert(eligible is None or (type(eligible) == list and all(type(x) == int for x in eligible)))
      assert(discloseMe is None or type(discloseMe) == bool)

      self.excludeMe = excludeMe
      self.exclude = exclude
      self.eligible = eligible
      self.discloseMe = discloseMe


class Subscribe:
   """
   """
   def __init__(self, match = None):
      assert(match is None or (type(match) == str and match in ['exact', 'prefix', 'wildcard']))
      self.match = match


class Register:
   """
   """
   def __init__(self, pkeys = None):
      assert(pkeys is None or type(pkeys) == list)
      self.pkeys = pkeys


class Call:
   """
   """
   def __init__(self, timeout = None):
      assert(timeout is None or type(timeout) == int)
      self.timeout = timeout
