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

import json
import datetime

from twisted.python import log
from twisted.internet import defer


from autobahn import util
from autobahn.wamp import auth
from autobahn.wamp import types
from autobahn.twisted.wamp import ApplicationSession, RouterSession
from autobahn.twisted.websocket import WampWebSocketServerProtocol, WampWebSocketServerFactory



class UserDb:
   """
   A fake user database.
   """

   def __init__(self):
      self._creds = {}

   def add(self, authid, authrole, secret, salt = None):
      if salt:
         key = auth.derive_key(secret, salt)
      else:
         key = secret
      self._creds[authid] = (salt, key, authrole)
      return self._creds[authid]

   def get(self, authid):
      ## we return a deferred to simulate an asynchronous lookup
      return defer.succeed(self._creds.get(authid, (None, None, None)))



class PendingAuth:
   """
   User for tracking pending authentications.
   """

   def __init__(self, key, session, authid, authrole, authmethod, authprovider):
      self.authid = authid
      self.authrole = authrole
      self.authmethod = authmethod
      self.authprovider = authprovider

      self.session = session
      self.timestamp = util.utcnow()
      self.nonce = util.newid()

      challenge_obj = {
         'authid': self.authid,
         'authrole': self.authrole,
         'authmethod': self.authmethod,
         'authprovider': self.authprovider,
         'session': self.session,
         'nonce': self.nonce,
         'timestamp': self.timestamp
      }
      self.challenge = json.dumps(challenge_obj)
      self.signature = auth.compute_wcs(key, self.challenge)



class MyRouterSession(RouterSession):
   """
   Our custom router session that authenticates via WAMP-CRA.
   """

   @defer.inlineCallbacks
   def onHello(self, realm, details):
      """
      Callback fired when client wants to attach session.
      """
      print("onHello: {} {}".format(realm, details))

      self._pending_auth = None

      if details.authmethods:
         for authmethod in details.authmethods:
            if authmethod == u"wampcra":

               ## lookup user in user DB
               salt, key, role = yield self.factory.userdb.get(details.authid)

               ## if user found ..
               if key:

                  ## setup pending auth
                  self._pending_auth = PendingAuth(key, details.pending_session,
                     details.authid, role, authmethod, "userdb")

                  ## send challenge to client
                  extra = {
                     'challenge': self._pending_auth.challenge
                  }

                  ## when using salted passwords, provide the client with
                  ## the salt and then PBKDF2 parameters used
                  if salt:
                     extra['salt'] = salt
                     extra['iterations'] = 1000
                     extra['keylen'] = 32

                  defer.returnValue(types.Challenge('wampcra', extra))

      ## deny client
      defer.returnValue(types.Deny())


   def onAuthenticate(self, signature, extra):
      """
      Callback fired when a client responds to an authentication challenge.
      """
      print("onAuthenticate: {} {}".format(signature, extra))

      ## if there is a pending auth, and the signature provided by client matches ..
      if self._pending_auth and signature == self._pending_auth.signature:

         ## accept the client
         return types.Accept(authid = self._pending_auth.authid,
            authrole = self._pending_auth.authrole,
            authmethod = self._pending_auth.authmethod,
            authprovider = self._pending_auth.authprovider)

      ## deny client
      return types.Deny()



class TimeService(ApplicationSession):
   """
   A simple time service application component.
   """

   def onJoin(self, details):
      print("session attached")

      def utcnow():
         now = datetime.datetime.utcnow()
         return now.strftime("%Y-%m-%dT%H:%M:%SZ")

      self.register(utcnow, 'com.timeservice.now')



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


   log.startLogging(sys.stdout)


   ## we use an Autobahn utility to install the "best" available Twisted reactor
   ##
   from autobahn.twisted.choosereactor import install_reactor
   reactor = install_reactor()
   if args.debug:
      print("Running on reactor {}".format(reactor))


   ## create a WAMP router factory
   ##
   from autobahn.twisted.wamp import RouterFactory
   router_factory = RouterFactory()


   ## create a user DB
   ##
   userdb = UserDb()
   userdb.add(authid = "peter", authrole = "user", secret = "secret1", salt = "salt123")
   userdb.add(authid = "joe", authrole = "user", secret = "secret2")


   ## create a WAMP router session factory
   ##
   from autobahn.twisted.wamp import RouterSessionFactory
   session_factory = RouterSessionFactory(router_factory)
   session_factory.session = MyRouterSession
   session_factory.userdb = userdb


   ## start an embedded application component ..
   ##
   component_config = types.ComponentConfig(realm = "realm1")
   component_session = TimeService(component_config)
   session_factory.add(component_session)


   ## create a WAMP-over-WebSocket transport server factory
   ##
   from autobahn.twisted.websocket import WampWebSocketServerFactory
   transport_factory = WampWebSocketServerFactory(session_factory, args.wsurl, debug = False, debug_wamp = args.debug)
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
   site.noisy = False
   site.log = lambda _: None


   ## start the WebSocket server from an endpoint
   ##
   server = serverFromString(reactor, args.websocket)
   server.listen(site)


   ## now enter the Twisted reactor loop
   ##
   reactor.run()
