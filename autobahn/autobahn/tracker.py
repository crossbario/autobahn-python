###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
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

from pprint import pformat

from zope.interface import implementer

from autobahn.util import Stopwatch
from autobahn.wamp.interfaces import ITracker



@implementer(ITracker)
class Tracker:

   def __init__(self, tracker, tracked):
      """
      """
      self.tracker = tracker
      self.tracked = tracked
      self._timings = {}
      self._stopwatch = Stopwatch()


   def track(self, key):
      """
      Track elapsed for key.

      :param key: Key under which to track the timing.
      :type key: str
      """
      self._timings[key] = self._stopwatch.elapsed()


   def diff(self, startKey, endKey, format = True):
      """
      Get elapsed difference between two previously tracked keys.

      :param startKey: First key for interval (older timestamp).
      :type startKey: str
      :param endKey: Second key for interval (younger timestamp).
      :type endKey: str
      :param format: If `True`, format computed time period and return string.
      :type format: bool

      :returns: float or str -- Computed time period in seconds (or formatted string).
      """
      if endKey in self._timings and startKey in self._timings:
         d = self._timings[endKey] - self._timings[startKey]
         if format:
            if d < 0.00001: # 10us
               s = "%d ns" % round(d * 1000000000.)
            elif d < 0.01: # 10ms
               s = "%d us" % round(d * 1000000.)
            elif d < 10: # 10s
               s = "%d ms" % round(d * 1000.)
            else:
               s = "%d s" % round(d)
            return s.rjust(8)
         else:
            return d
      else:
         if format:
            return "n.a.".rjust(8)
         else:
            return None


   def __getitem__(self, key):
      return self._timings.get(key, None)


   def __iter__(self):
      return self._timings.__iter__(self)


   def __str__(self):
      return pformat(self._timings)
