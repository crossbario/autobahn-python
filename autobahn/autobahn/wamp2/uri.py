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

import re


class Pattern:

   URI_TARGET_ENDPOINT = 1
   URI_TARGET_HANDLER = 2

   URI_TYPE_EXACT = 1
   URI_TYPE_PREFIX = 2
   URI_TYPE_WILDCARD = 3

   _URI_COMPONENT = re.compile(r"^[a-z][a-z0-9_]*$")
   _URI_NAMED_COMPONENT = re.compile(r"^<([a-z][a-z0-9_]*)>$")
   _URI_CONVERTED_COMPONENT = re.compile(r"^<([a-z]*):([a-z][a-z0-9_]*)>$")


   def __init__(self, uri, target):
      assert(type(uri) == str)
      assert(type(target) == int)
      assert(target in [Pattern.URI_TARGET_ENDPOINT, Pattern.URI_TARGET_HANDLER])

      components = uri.split('.')
      pl = []
      nc = {}
      i = 0
      for component in components:

         match = Pattern._URI_CONVERTED_COMPONENT.match(component)
         if match:
            ctype = match.groups()[0]
            if ctype not in ['string', 'int', 'suffix']:
               raise Exception("invalid URI")

            if ctype == 'suffix' and i != len(components) - 1:
               raise Exception("invalid URI")

            name = match.groups()[1]
            if name in nc:
               raise Exception("invalid URI")

            if ctype in ['string', 'suffix']:
               nc[name] = str
            elif ctype == 'int':
               nc[name] = int
            else:
               # should not arrive here
               raise Exception("logic error")

            pl.append("(?P<{}>[a-z0-9_]+)".format(name))
            continue

         match = Pattern._URI_NAMED_COMPONENT.match(component)
         if match:
            name = match.groups()[0]
            if name in nc:
               raise Exception("invalid URI")

            nc[name] = str
            pl.append("(?P<{}>[a-z][a-z0-9_]*)".format(name))
            continue

         match = Pattern._URI_COMPONENT.match(component)
         if match:
            pl.append(component)
            continue

         raise Exception("invalid URI")

      if nc:
         # URI pattern
         self._type = Pattern.URI_TYPE_WILDCARD
         p = "^" + "\.".join(pl) + "$"
         self._pattern = re.compile(p)
         self._names = nc
      else:
         # exact URI
         self._type = Pattern.URI_TYPE_EXACT
         self._pattern = None
         self._names = None
      self._uri = uri
      self._target = target


   def match(self, uri):
      if self._type == Pattern.URI_TYPE_EXACT:
         return {}
      elif self._type == Pattern.URI_TYPE_WILDCARD:
         match = self._pattern.match(uri)
         if match:
            kwargs = {}
            for key in self._names:
               val = match.group(key)
               val = self._names[key](val)
               kwargs[key] = val
            return kwargs
         else:
            raise Exception("no match")


   def is_endpoint(self):
      return self._target == Pattern.URI_TARGET_ENDPOINT


   def is_handler(self):
      return self._target == Pattern.URI_TARGET_HANDLER
