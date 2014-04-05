###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
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

from __future__ import absolute_import

__all__ = ['ApplicationSession',
           'ApplicationSessionFactory',
           'RouterSession',
           'RouterSessionFactory']

from autobahn.wamp import protocol


class ApplicationSession(protocol.ApplicationSession):
   """
   WAMP application session for Twisted-based applications.
   """


class ApplicationSessionFactory(protocol.ApplicationSessionFactory):
   """
   WAMP application session factory for Twisted-based applications.
   """


class RouterSession(protocol.RouterSession):
   """
   WAMP router session for Twisted-based applications.
   """


class RouterSessionFactory(protocol.RouterSessionFactory):
   """
   WAMP router session factory for Twisted-based applications.
   """


import sys
import traceback

from twisted.python import log
from autobahn.wamp.types import ComponentConfig
from twisted.internet.endpoints import clientFromString

from autobahn.twisted.websocket import WampWebSocketClientFactory


class ApplicationRunner:

   def __init__(self, endpoint, url, realm, extra = {}, debug = False,
      debug_wamp = False, debug_app = False):
      self.endpoint = endpoint
      self.url = url
      self.realm = realm
      self.extra = extra
      self.debug = debug
      self.debug_wamp = debug_wamp
      self.debug_app = debug_app
      self.make = None


   def run(self, make):
      from twisted.internet import reactor

      ## 0) start logging to console
      if self.debug or self.debug_wamp or self.debug_app:
         log.startLogging(sys.stdout)

      ## 1) factory for use ApplicationSession
      def create():
         cfg = ComponentConfig(self.realm, self.extra)
         try:
            session = make(cfg)
         except Exception as e:
            ## the app component could not be created .. fatal
            #print(traceback.format_exc())
            log.err()
            reactor.stop()

         session.debug_app = self.debug_app
         return session

      ## 2) create a WAMP-over-WebSocket transport client factory
      transport_factory = WampWebSocketClientFactory(create, url = self.url,
         debug = self.debug, debug_wamp = self.debug_wamp)

      ## 3) start the client from a Twisted endpoint
      client = clientFromString(reactor, self.endpoint)
      client.connect(transport_factory)

      ## 4) now enter the Twisted reactor loop
      reactor.run()
