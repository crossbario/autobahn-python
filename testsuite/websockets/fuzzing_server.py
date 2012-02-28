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

if sys.platform in ['freebsd8']:
   from twisted.internet import kqreactor
   kqreactor.install()

if sys.platform in ['win32']:
   from twisted.application.reactors import installReactor
   installReactor("iocp")

import sys, json
from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File
from autobahn.fuzzing import FuzzingServerFactory
from autobahn.websocket import listenWS


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   spec = json.loads(open("fuzzing_server_spec.json").read())

   ## fuzzing server
   fuzzer = FuzzingServerFactory(spec)
   listenWS(fuzzer)

   ## web server
   webdir = File(spec.get("webdir", "."))
   web = Site(webdir)
   reactor.listenTCP(spec.get("webport", 9090), web)

   log.msg("Using Twisted reactor class %s" % str(reactor.__class__))
   reactor.run()
