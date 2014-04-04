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

from twisted.python import log
from autobahn.wamp.types import ComponentConfig
from twisted.internet.endpoints import clientFromString

from autobahn.twisted.websocket import WampWebSocketClientFactory


class ApplicationRunner:

   def __init__(self, config):
      self.config = config
      self.make = None

      ep_config = config['router']

      ## generate Twisted endpoint descriptor from config
      if 'endpoint' in ep_config:
         ep = ep_config['endpoint']
         if 'type' in ep and ep['type'] in ['tcp']:
            if ep['type'] == 'tcp':
               if 'host' in ep and 'port' in ep:
                  host = ep['host']
                  port = int(ep['port'])
                  self.endpoint = "tcp:{}:{}".format(host, port)
               else:
                  raise Exception("missing host or port in TCP endpoint configuration")
            else:
               raise Exception("logic error")
         else:
            raise Exception("missing or invalid endpoint type")
      else:
         raise Exception("missing endpoint configuration")


   def run(self, make):
      ## 0) start logging to console
      log.startLogging(sys.stdout)

      def create():
         cfg = ComponentConfig(realm = self.config['router']['realm'])
         c = make(cfg)
         return c

      ## 2) create a WAMP-over-WebSocket transport client factory
      transport_factory = WampWebSocketClientFactory(create,
         url = self.config['router'].get('url', None),
         debug = self.config.get('debug', False))

      ## 3) start the client from a Twisted endpoint
      from twisted.internet import reactor
      client = clientFromString(reactor, self.endpoint)
      client.connect(transport_factory)

      ## 4) now enter the Twisted reactor loop
      reactor.run()
