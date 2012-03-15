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
from broadcast import BroadcastClientFactory, BroadcastServerFactory
from testee import TesteeClientFactory, TesteeServerFactory
from wsperfcontrol import WsPerfControlFactory
from wsperfmaster import WsPerfMasterFactory, WsPerfMasterUiFactory


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
      ['spec', 's', None, 'Test specification file [required in some modes].'],
      ['wsuri', 'w', None, 'WebSocket URI [required in some modes].'],
      ['key', 'k', None, 'Server private key file for secure WebSocket (WSS) [required in server modes for WSS].'],
      ['cert', 'c', None, 'Server certificate file for secure WebSocket (WSS) [required in server modes for WSS].'],
   ]

   optFlags = [
      ['debug', 'd', 'Debug output [default: off].']
   ]

   def postOptions(self):

      if not self['mode']:
         raise usage.UsageError, "a mode must be specified to run!"

      if not self['mode'] in WsTestOptions.MODES:
         raise usage.UsageError, "invalid mode %s" % self['mode']

      if self['mode'] in ['fuzzingclient',
                          'fuzzingserver',
                          'wsperfcontrol']:
         if not self['spec']:
            raise usage.UsageError, "mode needs a spec file!"

      if self['mode'] in ['echoclient',
                          'echoserver',
                          'broadcastclient',
                          'broadcastserver',
                          'testeeclient',
                          'testeeserver',
                          'wsperfcontrol']:
         if not self['wsuri']:
            raise usage.UsageError, "mode needs a WebSocket URI!"


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

   print "Using Twisted reactor class %s" % str(reactor.__class__)

   mode = str(o.opts['mode'])

   if mode in ['fuzzingclient', 'fuzzingserver']:

      spec = str(o.opts['spec'])
      spec = json.loads(open(spec).read())

      if mode == 'fuzzingserver':

         webdir = File(pkg_resources.resource_filename("wstest", "web/fuzzingserver"))
         web = Site(webdir)
         reactor.listenTCP(spec.get("webport", 8080), web)

         ## use TLS server key/cert from spec, but allow overriding from cmd line
         if not o.opts['key']:
            o.opts['key'] = spec.get('key', None)
         if not o.opts['cert']:
            o.opts['cert'] = spec.get('cert', None)

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
         factory.setProtocolOptions(failByDrop = False) # spec conformance
         listenWS(factory, createWssContext(o, factory))

      elif mode == 'testeeclient':
         factory = TesteeClientFactory(wsuri)
         factory.setProtocolOptions(failByDrop = False) # spec conformance
         connectWS(factory)

      else:
         raise Exception("logic error")

   elif mode in ['echoclient', 'echoserver']:

      wsuri = str(o.opts['wsuri'])

      if mode == 'echoserver':

         webdir = File(pkg_resources.resource_filename("wstest", "web/echoserver"))
         web = Site(webdir)
         reactor.listenTCP(8080, web)

         factory = EchoServerFactory(wsuri)
         listenWS(factory, createWssContext(o, factory))

      elif mode == 'echoclient':
         factory = EchoClientFactory(wsuri)
         connectWS(factory, createWssContext(o, factory))

      else:
         raise Exception("logic error")

   elif mode in ['broadcastclient', 'broadcastserver']:

      wsuri = str(o.opts['wsuri'])

      if mode == 'broadcastserver':

         webdir = File(pkg_resources.resource_filename("wstest", "web/broadcastserver"))
         web = Site(webdir)
         reactor.listenTCP(8080, web)

         factory = BroadcastServerFactory(wsuri)
         listenWS(factory, createWssContext(o, factory))

      elif mode == 'broadcastclient':
         factory = BroadcastClientFactory(wsuri)
         connectWS(factory, createWssContext(o, factory))

      else:
         raise Exception("logic error")

   elif mode == 'wsperfcontrol':

      wsuri = str(o.opts['wsuri'])

      spec = str(o.opts['spec'])
      spec = json.loads(open(spec).read())

      factory = WsPerfControlFactory(wsuri)
      factory.spec = spec
      factory.debugWsPerf = spec['options']['debug']
      factory.outfile = spec['options']['outfile']
      factory.sep = spec['options']['sep']
      factory.digits = spec['options']['digits']

      connectWS(factory, createWssContext(o, factory))

   elif mode == 'wsperfmaster':

      ## WAMP Server for wsperf slaves
      ##
      wsperf = WsPerfMasterFactory("ws://localhost:9090")
      wsperf.debug = False
      wsperf.debugWsPerf = False
      listenWS(wsperf)

      ## Web Server for UI static files
      ##
      webdir = File(pkg_resources.resource_filename("wstest", "web/wsperfmaster"))
      web = Site(webdir)
      reactor.listenTCP(8080, web)

      ## WAMP Server for UI
      ##
      wsperfUi = WsPerfMasterUiFactory("ws://localhost:9091")
      wsperfUi.debug = False
      wsperfUi.debugWamp = False
      listenWS(wsperfUi)

      ## Connect servers
      ##
      wsperf.uiFactory = wsperfUi
      wsperfUi.slaveFactory = wsperf

   elif mode in ['testeeclient', 'testeeserver']:

      raise Exception("not yet implemented")

   else:

      raise Exception("logic error")

   reactor.run()
