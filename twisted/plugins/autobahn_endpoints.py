###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from __future__ import absolute_import

from zope.interface import implementer

from twisted.plugin import IPlugin
from twisted.internet.interfaces import IStreamServerEndpointStringParser, \
    IStreamServerEndpoint, \
    IStreamClientEndpoint

try:
    from twisted.internet.interfaces import IStreamClientEndpointStringParserWithReactor
    _HAS_REACTOR_ARG = True
except ImportError:
    _HAS_REACTOR_ARG = False
    from twisted.internet.interfaces import IStreamClientEndpointStringParser as \
        IStreamClientEndpointStringParserWithReactor

from twisted.internet.endpoints import serverFromString, clientFromString

from autobahn.twisted.websocket import WrappingWebSocketServerFactory, \
    WrappingWebSocketClientFactory


def _parseOptions(options):
    opts = {}

    if 'url' not in options:
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

        # The present endpoint plugin is intended to be used as in the
        # following for running a streaming protocol over WebSocket over
        # an underlying stream transport.
        #
        # endpoint = serverFromString(reactor,
        # "autobahn:tcp\:9000\:interface\=0.0.0.0:url=ws\://localhost\:9000:compress=false"
        #
        # This will result in `parseStreamServer` to be called will
        #
        # description == tcp:9000:interface=0.0.0.0
        #
        # and
        #
        # options == {'url': 'ws://localhost:9000', 'compress': 'false'}
        #
        # Essentially, we are using the `\:` escape to coerce the endpoint descriptor
        # of the underlying stream transport into one (first) positional argument.
        #
        # Note that the `\:` within "url" is another form of escaping!
        #
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
        return self._endpoint.listen(WrappingWebSocketServerFactory(protocolFactory, reactor=self._reactor, **self._options))


# note that for older Twisted before the WithReactor variant, we
# import it under that name so we can share (most of) this
# implementation...
@implementer(IPlugin)
@implementer(IStreamClientEndpointStringParserWithReactor)
class AutobahnClientParser(object):
    prefix = "autobahn"

    def parseStreamClient(self, *args, **options):
        if _HAS_REACTOR_ARG:
            reactor = args[0]
            if len(args) != 2:
                raise RuntimeError("autobahn: client plugin takes exactly one positional argument")
            description = args[1]
        else:
            from twisted.internet import reactor
            if len(args) != 1:
                raise RuntimeError("autobahn: client plugin takes exactly one positional argument")
            description = args[0]
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
        return self._endpoint.connect(WrappingWebSocketClientFactory(protocolFactory, reactor=self._reactor, **self._options))


autobahnServerParser = AutobahnServerParser()
autobahnClientParser = AutobahnClientParser()
