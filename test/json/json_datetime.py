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

import json, datetime
from json.decoder import scanstring, py_scanstring
from json.scanner import make_scanner, py_make_scanner

ISO_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


## There are a couple of problems with this code. The main one is a consequence
## of the lack of parse_string argument in JSONDecoder constructor in Python.
##
## 1) it does not support the whole ISO 8601
## 2) JSONDecoder can take i.e. parse_float, but not parse_string in __init__
##    to hook in custom string parser.
## 3) JSONDecoder has a self.parse_string internally, but override only works
##    when using py_make_scanner, not C-based make_scanner
## 4) The custom_parse_string is naive: it will just try to convert any string
##    to datetime, and if it works, will provide that.
##


class CustomJSONEncoder(json.JSONEncoder):

   def default(self, obj):
      if isinstance(obj, datetime.datetime):
         return obj.strftime(ISO_TIMESTAMP_FORMAT)
      else:
         return json.JSONEncoder.default(self, obj)


def custom_parse_string(string, idx, encoding, strict):
   obj = scanstring(string, idx, encoding, strict)
   if type(obj[0]) in [str, unicode]:
      try:
         dt = datetime.datetime.strptime(obj[0], ISO_TIMESTAMP_FORMAT)
         return [dt, obj[1]]
      except:
         pass
   return obj


class CustomJSONDecoder(json.JSONDecoder):

   def __init__(self, encoding=None, object_hook=None, parse_float=None,
                parse_int=None, parse_constant=None, strict=True,
                object_pairs_hook=None):
      json.JSONDecoder.__init__(self, encoding, object_hook, parse_float, parse_int, parse_constant, strict, object_pairs_hook)
      self.parse_string = custom_parse_string
      #self.scan_once = make_scanner(self)  # using C-based variant does not work
      self.scan_once = py_make_scanner(self)


if __name__ == '__main__':

   objs = [
        "sdlkjfh",
        datetime.datetime.utcnow(),
        [datetime.datetime.utcnow(), 5, 6],
        {'foo': 23,
        'goo': datetime.datetime.utcnow(),
        'zoo': [1, 2, 3, datetime.datetime.utcnow(), 4, 5],
        'koo': {'x1': datetime.datetime.utcnow(), 'x2': 666}}]

   for o in objs:
      print o
      s = json.dumps(o, cls = CustomJSONEncoder)
      print s
      o2 = json.loads(s, cls = CustomJSONDecoder)
      print o2
