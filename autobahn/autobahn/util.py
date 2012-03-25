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

import datetime
import time
import random

UTC_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def utcnow():
   """
   Get current time in UTC as ISO 8601 string.
   """
   now = datetime.datetime.utcnow()
   return now.strftime(UTC_TIMESTAMP_FORMAT)


def parseutc(s):
   """
   Parse an ISO 8601 combined date and time string, like i.e. 2011-11-23T12:23Z
   into a UTC datetime instance.
   """
   try:
      return datetime.datetime.strptime(s, UTC_TIMESTAMP_FORMAT)
   except:
      return None


def utcstr(dt):
   """
   Convert an UTC datetime instance into an ISO 8601 combined date and time,
   like i.e. 2011-11-23T12:23Z
   """
   try:
      return dt.strftime(UTC_TIMESTAMP_FORMAT)
   except:
      return None


def newid():
   """
   Generate a new random object ID.
   """
   return ''.join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_") for i in xrange(16)])
