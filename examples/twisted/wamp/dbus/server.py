###############################################################################
##
##  Copyright 2012 Tavendo GmbH
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
from twisted.internet import reactor, defer
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import listenWS

from autobahn.wamp import exportRpc, \
                          WampServerFactory, \
                          WampCraServerProtocol



class DbusServerProtocol(WampCraServerProtocol):

   ## our pseudo user/permissions database
   USERS = {'user1': 'secret',
            'user2': 'geheim'}

   def onSessionOpen(self):

      ## override global client auth options
      self.clientAuthTimeout = 0
      self.clientAuthAllowAnonymous = True

      ## call base class method
      WampCraServerProtocol.onSessionOpen(self)


   def getAuthPermissions(self, authKey, authExtra):
      if authKey is None:
         ## notification issuer is only allowed to publish to topics
         ## and retrieve list of users
         pms = {'pubsub': [{'uri': 'http://example.com/topics/',
                                    'prefix': True,
                                    'pub': True,
                                    'sub': False}],
                 'rpc': [{'uri': 'http://example.com/procedures/getusers',
                          'call': True}]}
         return {'permissions': pms}
      else:
         ## desktop notification client is only allowed to subscribe to topics
         ##  http://example.com/topics/all
         ##  http://example.com/topics/<user>
         ##
         pms = {'pubsub': [{'uri': 'http://example.com/topics/all',
                                    'prefix': False,
                                    'pub': False,
                                    'sub': True},
                            {'uri': 'http://example.com/topics/%s' % authKey,
                                    'prefix': False,
                                    'pub': False,
                                    'sub': True}],
                 'rpc': []}
         return {'permissions': pms}


   def getAuthSecret(self, authKey):
      ## return the auth secret for the given auth key or None when the auth key
      ## does not exist
      return self.USERS.get(authKey, None)


   def onAuthenticated(self, authKey, permissions):
      ## fired when authentication succeeds

      ## register PubSub topics from the auth permissions
      self.registerForPubSubFromPermissions(perms['permissions'])

      ## register RPC endpoints (for now do that manually, keep in sync with perms)
      if authKey is None:
         self.registerForRpc(self, 'http://example.com/procedures/',
                             [MyServerProtocol.getUsers])


   @exportRpc("getusers")
   def getUsers(self):
      return self.USERS.keys()



if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   factory = WampServerFactory("ws://localhost:9000", debugWamp = debug)
   factory.protocol = DbusServerProtocol
   listenWS(factory)

   webdir = File(".")
   web = Site(webdir)
   reactor.listenTCP(8080, web)

   reactor.run()
