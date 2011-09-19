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

import sys
from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File
from autobahn.fuzzing import FuzzingServerFactory


if __name__ == '__main__':

   log.startLogging(sys.stdout)

   ## fuzzing server
   fuzzer = FuzzingServerFactory(debug = False, outdir = "reports/clients")
   #fuzzer.requireMaskedClientFrames = False
   #fuzzer.utf8validateIncoming = False
   reactor.listenTCP(9001, fuzzer)

   ## web server
   webdir = File(".")
   web = Site(webdir)
   reactor.listenTCP(9090, web)

   reactor.run()
