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

from __future__ import absolute_import

from zope.interface import implementer

from twisted.plugin import IPlugin
from twisted.internet.interfaces import IStreamServerEndpointStringParser, \
                                        IStreamServerEndpoint, \
                                        IStreamClientEndpointStringParser, \
                                        IStreamClientEndpoint

from twisted.internet.endpoints import serverFromString, clientFromString

from autobahn.twisted.websocket import WrappingWebSocketServerFactory, \
                                       WrappingWebSocketClientFactory


def _parseOptions(options):
   opts = {}

   if not 'url' in options:
      raise Exception("URL needed")
   else:
      opts['url'] = options['url']

   if 'compression' in options:
      value = options['compression'].lower().strip()
      if value == 'true':
         opts['enableCompression'] = True
      elif value == 'false':
         opts['enableCompression'] = False
      else:
         raise Exception("invalid value '{}' for compression".format(value))

   if 'autofrag' in options:
      try:
         value = int(options['autofrag'])
      except:
         raise Exception("invalid value '{}' for autofrag".format(options['autofrag']))

      if value < 0:
         raise Exception("negative value '{}' for autofrag".format(value))

      opts['autoFragmentSize'] = value

   return opts


@implementer(IPlugin)
@implementer(IStreamServerEndpointStringParser)
class AutobahnServerParser(object):

   prefix = "autobahn"

   def parseStreamServer(self, reactor, description, **options):
      ## "description" is the underyling stream descriptor like
      ## eg "tcp:9000:interface=0.0.0.0" while "options" contains
      ## the rest, eg {'url': 'ws://localhost:9000'}
      ##
      opts = _parseOptions(options)
      endpoint = serverFromString(reactor, description)
      return AutobahnServerEndpoint(endpoint, opts)


@implementer(IPlugin)
@implementer(IStreamServerEndpoint)
class AutobahnServerEndpoint(object):

   def __init__(self, endpoint, options):
      self._endpoint = endpoint
      self._options = options

   def listen(self, protocolFactory):
      return self._endpoint.listen(WrappingWebSocketServerFactory(protocolFactory, **self._options))


@implementer(IPlugin)
@implementer(IStreamClientEndpointStringParser)
class AutobahnClientParser(object):

   prefix = "autobahn"

   def parseStreamClient(self, reactor, description, **options):
      print("*"*10)
      print(description)
      opts = _parseOptions(options)
      endpoint = clientFromString(reactor, description)
      return AutobahnClientEndpoint(endpoint, opts)


@implementer(IPlugin)
@implementer(IStreamClientEndpoint)
class AutobahnClientEndpoint(object):

   def __init__(self, endpoint, options):
      self._endpoint = endpoint
      self._options = options

   def listen(self, protocolFactory):
      return self._endpoint.connect(WrappingWebSocketClientFactory(protocolFactory, **self._options))


autobahnServerParser = AutobahnServerParser()
autobahnClientParser = AutobahnClientParser()
