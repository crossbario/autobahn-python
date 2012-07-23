###############################################################################
##
##  Copyright 2011,2012 Tavendo GmbH
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

try:
   import pkg_resources
   version = pkg_resources.require("Autobahn")[0].version
except:
   ## i.e. no setuptools or no package installed ..
   version = "?.?.?"

import util
import useragent
import httpstatus
import utf8validator
import xormasker
import websocket
import resource
import prefixmap
import wamp
