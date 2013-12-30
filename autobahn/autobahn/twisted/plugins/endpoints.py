###############################################################################
##
##  Copyright (C) 2013 Tavendo GmbH
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

from zope.interface import implementer

from twisted.plugin import IPlugin
from twisted.internet.interfaces import IStreamServerEndpointStringParser, IStreamServerEndpoint
from twisted.internet.endpoints import serverFromString
from txsockjs.factory import SockJSFactory


@implementer(IPlugin)
@implementer(IStreamServerEndpointStringParser)
class AutobahnServerParser(object):

   prefix = "autobahn"

   def parseStreamServer(self, reactor, description, **options):
      if 'websocket' in options:
         options['websocket'] = options['websocket'].lower() == "true"
      if 'cookie_needed' in options:
         options['cookie_needed'] = options['cookie_needed'].lower() == "true"
      if 'heartbeat' in options:
         options['heartbeat'] = int(options['websocket'])
      if 'timeout' in options:
         options['timeout'] = int(options['timeout'])
      if 'streaming_limit' in options:
         options['streaming_limit'] = int(options['streaming_limit'])
      endpoint = serverFromString(reactor, description)
      return AutobahnServerEndpoint(endpoint, options)


@implementer(IPlugin)
@implementer(IStreamServerEndpoint)
class AutobahnServerEndpoint(object):

   def __init__(self, endpoint, options):
      self._endpoint = endpoint
      self._options = options

   def listen(self, protocolFactory):
      return self._endpoint.listen(SockJSFactory(protocolFactory, self._options))


autobahnServerParser = AutobahnServerParser()
