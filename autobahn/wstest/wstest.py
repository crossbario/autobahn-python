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

import sys, os, json, pkg_resources

from twisted.python import log, usage
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import connectWS, listenWS
from autobahn.fuzzing import FuzzingClientFactory, FuzzingServerFactory

from echo import EchoClientFactory, EchoServerFactory
from testee import TesteeClientFactory, TesteeServerFactory


class WsTestOptions(usage.Options):
   MODES = ['echoserver',
            'echoclient',
            'broadcastclient',
            'broadcastserver',

            'fuzzingserver',
            'fuzzingclient',
            'testeeserver',
            'testeeclient',

            'wsperfcontrol',
            'wsperfmaster',

            'wampserver',
            'wampclient']

   optParameters = [
      ['mode', 'm', None, 'Test mode, one of: %s [required]' % ', '.join(MODES)],
      ['spec', 's', None, 'Test specification file [required in fuzzing modes].'],
      ['wsuri', 'w', None, 'WebSocket URI [required in echo modes].'],
      ['key', 'k', None, 'Server private key file for secure WebSocket (WSS) [required in server modes for WSS].'],
      ['cert', 'c', None, 'Server certificate file for secure WebSocket (WSS) [required in server modes for WSS].'],
   ]

   optFlags = [
      ['debug', 'd', 'Debug wsperf commander/protocol [default: off].']
   ]

   def postOptions(self):
      if not self['mode']:
         raise usage.UsageError, "a mode must be specified to run!"
      if not self['mode'] in WsTestOptions.MODES:
         raise usage.UsageError, "invalid mode %s" % self['mode']
      if self['mode'] in ['fuzzingclient', 'fuzzingserver']:
         if not self['spec']:
            raise usage.UsageError, "fuzzing modes need a test specification file!"
      elif self['mode'] in ['echoclient', 'echoserver', 'testeeclient', 'testeeserver']:
         if not self['wsuri']:
            raise usage.UsageError, "echo, testee modes need a WebSocket URI!"


OPENSSL_HELP = """
To generate server test key/certificate:

openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -days 3650 -in server.csr -signkey server.key -out server.crt

Then start wstest:

wstest -m echoserver -w wss://localhost:9000 -k server.key -c server.crt
"""

def createWssContext(o, factory):
   if factory.isSecure:

      try:
         from twisted.internet import ssl
      except ImportError, e:
         print "You need OpenSSL/pyOpenSSL installed for secure WebSockets (wss)!"
         sys.exit(1)

      if o.opts['key'] is None:
         print "Server key and certificate required for WSS"
         print OPENSSL_HELP
         sys.exit(1)
      if o.opts['cert'] is None:
         print "Server key and certificate required for WSS"
         print OPENSSL_HELP
         sys.exit(1)

      key = str(o.opts['key'])
      cert = str(o.opts['cert'])
      contextFactory = ssl.DefaultOpenSSLContextFactory(key, cert)

   else:
      contextFactory = None

   return contextFactory


def run():

   o = WsTestOptions()
   try:
      o.parseOptions()
   except usage.UsageError, errortext:
      print '%s %s\n' % (sys.argv[0], errortext)
      print 'Try %s --help for usage details\n' % sys.argv[0]
      sys.exit(1)

   log.startLogging(sys.stdout)
   log.msg("Using Twisted reactor class %s" % str(reactor.__class__))

   mode = str(o.opts['mode'])

   if mode in ['fuzzingclient', 'fuzzingserver']:

      spec = str(o.opts['spec'])
      spec = json.loads(open(spec).read())

      if mode == 'fuzzingserver':

         webdir = File(pkg_resources.resource_filename("wstest", "web/fuzzingserver"))
         web = Site(webdir)
         reactor.listenTCP(spec.get("webport", 9090), web)

         factory = FuzzingServerFactory(spec)
         listenWS(factory, createWssContext(o, factory))

      elif mode == 'fuzzingclient':
         factory = FuzzingClientFactory(spec)
         # no connectWS done here, since this is done within
         # FuzzingClientFactory automatically to orchestrate tests

      else:
         raise Exception("logic error")

   elif mode in ['testeeclient', 'testeeserver']:

      wsuri = str(o.opts['wsuri'])

      if mode == 'testeeserver':
         factory = TesteeServerFactory(wsuri)
         listenWS(factory, createWssContext(o, factory))

      elif mode == 'testeeclient':
         factory = TesteeClientFactory(wsuri)
         # no connectWS done here, since this is done within
         # TesteeClientFactory automatically to orchestrate tests

      else:
         raise Exception("logic error")

   elif mode in ['echoclient', 'echoserver']:

      wsuri = str(o.opts['wsuri'])

      if mode == 'echoserver':
         factory = EchoServerFactory(wsuri)
         listenWS(factory, createWssContext(o, factory))

      elif mode == 'echoclient':
         factory = EchoClientFactory(wsuri)
         connectWS(factory, createWssContext(o, factory))

      else:
         raise Exception("logic error")

   else:

      raise Exception("not yet implemented")

   reactor.run()
