###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
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

from autobahn.twisted.wamp import ApplicationSession


class TimeService(ApplicationSession):
   """
   A simple time service application component.
   """

   def __init__(self, realm = "realm1"):
      ApplicationSession.__init__(self)
      self._realm = realm


   def onConnect(self):
      self.join(self._realm)


   def onJoin(self, details):

      def utcnow():
         now = datetime.datetime.utcnow()
         return now.strftime("%Y-%m-%dT%H:%M:%SZ")

      self.register(utcnow, 'com.timeservice.now')



from twisted.python import log
from autobahn.twisted.websocket import WampWebSocketServerProtocol, WampWebSocketServerFactory
from twisted.internet.defer import Deferred

import json
import urllib
import Cookie

from autobahn.util import newid, utcnow
from autobahn.websocket import http


class ServerProtocol(WampWebSocketServerProtocol):

   def onConnect(self, request):
      protocol, headers = WampWebSocketServerProtocol.onConnect(self, request)

      ## our cookie tracking ID
      self._cbtid = None

      ## see if there already is a cookie set ..
      if request.headers.has_key('cookie'):
         try:
            cookie = Cookie.SimpleCookie()
            cookie.load(str(request.headers['cookie']))
         except Cookie.CookieError:
            pass
         else:
            if cookie.has_key('cbtid'):
               cbtid = cookie['cbtid'].value
               if self.factory._cookies.has_key(cbtid):
                  self._cbtid = cbtid
                  log.msg("Cookie already set: %s" % self._cbtid)

      ## if no cookie is set, create a new one ..
      if self._cbtid is None:

         self._cbtid = newid()
         maxAge = 86400

         cbtData = {'created': utcnow(),
                    'authenticated': None,
                    'maxAge': maxAge,
                    'connections': set()}

         self.factory._cookies[self._cbtid] = cbtData

         ## do NOT add the "secure" cookie attribute! "secure" refers to the
         ## scheme of the Web page that triggered the WS, not WS itself!!
         ##
         headers['Set-Cookie'] = 'cbtid=%s;max-age=%d' % (self._cbtid, maxAge)
         log.msg("Setting new cookie: %s" % self._cbtid)

      ## add this WebSocket connection to the set of connections
      ## associated with the same cookie
      self.factory._cookies[self._cbtid]['connections'].add(self)

      self._authenticated = self.factory._cookies[self._cbtid]['authenticated']

      ## accept the WebSocket connection, speaking subprotocol `protocol`
      ## and setting HTTP headers `headers`
      return (protocol, headers)



from autobahn.wamp.protocol import RouterSession
from autobahn.wamp import types


class MyRouterSession(RouterSession):

   def onOpen(self, transport):
      RouterSession.onOpen(self, transport)
      print "transport authenticated: {}".format(self._transport._authenticated)


   def onHello(self, realm, details):
      print "onHello: {} {}".format(realm, details)
      if self._transport._authenticated is not None:
         return types.Accept(authid = self._transport._authenticated)
      else:
         return types.Challenge("mozilla-persona")
      return accept


   def onAuthenticate(self, signature, extra):
      print "onAuthenticate: {} {}".format(signature, extra)

      dres = Deferred()

      ## The client did it's Mozilla Persona authentication thing
      ## and now wants to verify the authentication and login.
      assertion = signature
      audience = 'http://localhost:8080/'

      ## To verify the authentication, we need to send a HTTP/POST
      ## to Mozilla Persona. When successful, Persona will send us
      ## back something like:

      # {
      #    "audience": "http://192.168.1.130:8080/",
      #    "expires": 1393681951257,
      #    "issuer": "gmail.login.persona.org",
      #    "email": "tobias.oberstein@gmail.com",
      #    "status": "okay"
      # }

      headers = {'Content-Type': 'application/x-www-form-urlencoded'}
      body = urllib.urlencode({'audience': audience, 'assertion': assertion})

      from twisted.web.client import getPage
      d = getPage(url = "https://verifier.login.persona.org/verify",
                  method = 'POST',
                  postdata = body,
                  headers = headers)

      log.msg("Authentication request sent.")

      def done(res):
         res = json.loads(res)
         try:
            if res['status'] == 'okay':
               ## Mozilla Persona successfully authenticated the user

               ## remember the user's email address. this marks the cookie as
               ## authenticated
               self._transport.factory._cookies[self._transport._cbtid]['authenticated'] = res['email']

               log.msg("Authenticated user {}".format(res['email']))
               dres.callback(types.Accept(authid = res['email']))
            else:
               log.msg("Authentication failed!")
               dres.callback(types.Deny())
         except Exception as e:
            print "ERRR", e

      def error(err):
         log.msg("Authentication request failed: {}".format(err.value))
         dres.callback(types.Deny())

      d.addCallbacks(done, error)

      return dres


if __name__ == '__main__':

   import sys, argparse

   from twisted.python import log
   from twisted.internet.endpoints import serverFromString


   ## parse command line arguments
   ##
   parser = argparse.ArgumentParser()

   parser.add_argument("-d", "--debug", action = "store_true",
                       help = "Enable debug output.")

   parser.add_argument("-c", "--component", type = str, default = None,
                       help = "Start WAMP-WebSocket server with this application component, e.g. 'timeservice.TimeServiceBackend', or None.")

   parser.add_argument("--websocket", type = str, default = "tcp:8080",
                       help = 'WebSocket server Twisted endpoint descriptor, e.g. "tcp:9000" or "unix:/tmp/mywebsocket".')

   parser.add_argument("--wsurl", type = str, default = "ws://localhost:8080",
                       help = 'WebSocket URL (must suit the endpoint), e.g. "ws://localhost:9000".')

   args = parser.parse_args()


   ## start Twisted logging to stdout
   ##
   if True or args.debug:
      log.startLogging(sys.stdout)


   ## we use an Autobahn utility to install the "best" available Twisted reactor
   ##
   from autobahn.twisted.choosereactor import install_reactor
   reactor = install_reactor()
   if args.debug:
      print("Running on reactor {}".format(reactor))


   ## create a WAMP router factory
   ##
   from autobahn.wamp.router import RouterFactory
   router_factory = RouterFactory()


   ## create a WAMP router session factory
   ##
   from autobahn.twisted.wamp import RouterSessionFactory
   session_factory = RouterSessionFactory(router_factory)
   session_factory.session = MyRouterSession


   ## start an embedded application component ..
   ##
   session_factory.add(TimeService())


   ## create a WAMP-over-WebSocket transport server factory
   ##
   from autobahn.twisted.websocket import WampWebSocketServerFactory
   transport_factory = WampWebSocketServerFactory(session_factory, args.wsurl, debug = args.debug)
   transport_factory.protocol = ServerProtocol
   transport_factory._cookies = {}

   transport_factory.setProtocolOptions(failByDrop = False)


   from twisted.web.server import Site
   from twisted.web.static import File
   from autobahn.twisted.resource import WebSocketResource

   ## we serve static files under "/" ..
   root = File(".")

   ## .. and our WebSocket server under "/ws"
   resource = WebSocketResource(transport_factory)
   root.putChild("ws", resource)

   ## run both under one Twisted Web Site
   site = Site(root)

   ## start the WebSocket server from an endpoint
   ##
   server = serverFromString(reactor, args.websocket)
   server.listen(site)


   ## now enter the Twisted reactor loop
   ##
   reactor.run()
