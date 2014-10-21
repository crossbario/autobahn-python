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
         raise Exception("invalid value '{0}' for compression".format(value))

   if 'autofrag' in options:
      try:
         value = int(options['autofrag'])
      except:
         raise Exception("invalid value '{0}' for autofrag".format(options['autofrag']))

      if value < 0:
         raise Exception("negative value '{0}' for autofrag".format(value))

      opts['autoFragmentSize'] = value

   if 'subprotocol' in options:
      value = options['subprotocol'].lower().strip()
      opts['subprotocol'] = value

   if 'debug' in options:
      value = options['debug'].lower().strip()
      if value == 'true':
         opts['debug'] = True
      elif value == 'false':
         opts['debug'] = False
      else:
         raise Exception("invalid value '{0}' for debug".format(value))

   return opts


@implementer(IPlugin)
@implementer(IStreamServerEndpointStringParser)
class AutobahnServerParser(object):

   prefix = "autobahn"

   def parseStreamServer(self, reactor, description, **options):

      ## The present endpoint plugin is intended to be used as in the
      ## following for running a streaming protocol over WebSocket over
      ## an underlying stream transport.
      ##
      ##  endpoint = serverFromString(reactor,
      ##    "autobahn:tcp\:9000\:interface\=0.0.0.0:url=ws\://localhost\:9000:compress=false"
      ##
      ## This will result in `parseStreamServer` to be called will
      ##
      ##   description == tcp:9000:interface=0.0.0.0
      ##
      ## and
      ##
      ##   options == {'url': 'ws://localhost:9000', 'compress': 'false'}
      ##
      ## Essentially, we are using the `\:` escape to coerce the endpoint descriptor
      ## of the underyling stream transport into one (first) positional argument.
      ##
      ## Note that the `\:` within "url" is another form of escaping!
      ##
      opts = _parseOptions(options)
      endpoint = serverFromString(reactor, description)
      return AutobahnServerEndpoint(reactor, endpoint, opts)


@implementer(IPlugin)
@implementer(IStreamServerEndpoint)
class AutobahnServerEndpoint(object):

   def __init__(self, reactor, endpoint, options):
      self._reactor = reactor
      self._endpoint = endpoint
      self._options = options

   def listen(self, protocolFactory):
      return self._endpoint.listen(WrappingWebSocketServerFactory(protocolFactory, reactor = self._reactor, **self._options))


@implementer(IPlugin)
@implementer(IStreamClientEndpointStringParser)
class AutobahnClientParser(object):

   prefix = "autobahn"

## <oberstet> Is there are particular reason why "plugin.parseStreamServer" provides a "reactor" argument while "plugin.parseStreamClient" does not?
## <oberstet> http://twistedmatrix.com/trac/browser/tags/releases/twisted-13.2.0/twisted/internet/endpoints.py#L1396
## <oberstet> http://twistedmatrix.com/trac/browser/tags/releases/twisted-13.2.0/twisted/internet/endpoints.py#L1735

## => http://twistedmatrix.com/trac/ticket/4956
## => https://twistedmatrix.com/trac/ticket/5069

#   def parseStreamClient(self, reactor, description, **options):
   def parseStreamClient(self, description, **options):
      from twisted.internet import reactor
      opts = _parseOptions(options)
      endpoint = clientFromString(reactor, description)
      return AutobahnClientEndpoint(reactor, endpoint, opts)


@implementer(IPlugin)
@implementer(IStreamClientEndpoint)
class AutobahnClientEndpoint(object):

   def __init__(self, reactor, endpoint, options):
      self._reactor = reactor
      self._endpoint = endpoint
      self._options = options

   def connect(self, protocolFactory):
      return self._endpoint.connect(WrappingWebSocketClientFactory(protocolFactory, reactor = self._reactor, **self._options))


autobahnServerParser = AutobahnServerParser()
autobahnClientParser = AutobahnClientParser()
