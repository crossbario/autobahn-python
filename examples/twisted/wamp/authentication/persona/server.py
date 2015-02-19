###############################################################################
#
# The MIT License (MIT)
# 
# Copyright (c) Tavendo GmbH
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

import datetime
import json
import urllib
import Cookie

from autobahn.twisted.wamp import ApplicationSession

from twisted.python import log
from twisted.internet.defer import Deferred

from autobahn.twisted.websocket import WampWebSocketServerProtocol, WampWebSocketServerFactory
from autobahn.twisted.wamp import RouterSession
from autobahn.wamp import types

from autobahn.util import newid, utcnow
from autobahn.websocket import http


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


class ServerProtocol(WampWebSocketServerProtocol):

    """
    A WAMP-WebSocket transport that supports Cookie based authentication.
    """

    # authid -> cookie -> set(connection)

    def onConnect(self, request):
        protocol, headers = WampWebSocketServerProtocol.onConnect(self, request)

        # our cookie tracking ID
        self._cbtid = None

        # see if there already is a cookie set ..
        if 'cookie' in request.headers:
            try:
                cookie = Cookie.SimpleCookie()
                cookie.load(str(request.headers['cookie']))
            except Cookie.CookieError:
                pass
            else:
                if 'cbtid' in cookie:
                    cbtid = cookie['cbtid'].value
                    if cbtid in self.factory._cookies:
                        self._cbtid = cbtid
                        log.msg("Cookie already set: %s" % self._cbtid)

        # if no cookie is set, create a new one ..
        if self._cbtid is None:

            self._cbtid = newid()
            maxAge = 86400

            cbtData = {'created': utcnow(),
                       'authenticated': None,
                       'maxAge': maxAge,
                       'connections': set()}

            self.factory._cookies[self._cbtid] = cbtData

            # do NOT add the "secure" cookie attribute! "secure" refers to the
            # scheme of the Web page that triggered the WS, not WS itself!!
            ##
            headers['Set-Cookie'] = 'cbtid=%s;max-age=%d' % (self._cbtid, maxAge)
            log.msg("Setting new cookie: %s" % self._cbtid)

        # add this WebSocket connection to the set of connections
        # associated with the same cookie
        self.factory._cookies[self._cbtid]['connections'].add(self)

        self._authenticated = self.factory._cookies[self._cbtid]['authenticated']

        # accept the WebSocket connection, speaking subprotocol `protocol`
        # and setting HTTP headers `headers`
        return (protocol, headers)


class MyRouterSession(RouterSession):

    def onOpen(self, transport):
        """
        Callback fired when transport (WebSocket connection) was established.
        """
        RouterSession.onOpen(self, transport)
        print("MyRouterSession.onOpen: transport authenticated = {}".format(self._transport._authenticated))

    def onHello(self, realm, details):
        """
        Callback fired when client wants to attach session.
        """
        print("MyRouterSession.onHello: {} {}".format(realm, details))

        for authmethod in details.authmethods:
            if authmethod == u"cookie" and self._transport._authenticated is not None:
                # already authenticated via Cookie on transport
                return types.Accept(authid=self._transport._authenticated, authrole="user", authmethod="cookie")
            elif authmethod == u"mozilla-persona":
                # not yet authenticated: send challenge
                return types.Challenge("mozilla-persona")

        return types.Deny()

    def onLeave(self, details):
        """
        Callback fired when a client session leaves.
        """
        if details.reason == "wamp.close.logout":
            # if asked to logout, set cookie to "not authenticated" ..
            cookie = self._transport.factory._cookies[self._transport._cbtid]
            cookie['authenticated'] = None

            # .. and kill all currently connected clients (for the cookie)
            for proto in cookie['connections']:
                proto.sendClose()

    def onAuthenticate(self, signature, extra):
        """
        Callback fired when a client responds to an authentication challenge.
        """
        print("onAuthenticate: {} {}".format(signature, extra))

        dres = Deferred()

        # The client did it's Mozilla Persona authentication thing
        # and now wants to verify the authentication and login.
        assertion = signature
        audience = 'http://127.0.0.1:8080/'

        # To verify the authentication, we need to send a HTTP/POST
        # to Mozilla Persona. When successful, Persona will send us
        # back something like:

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
        d = getPage(url="https://verifier.login.persona.org/verify",
                    method='POST',
                    postdata=body,
                    headers=headers)

        log.msg("Authentication request sent.")

        def done(res):
            res = json.loads(res)
            try:
                if res['status'] == 'okay':
                    # Mozilla Persona successfully authenticated the user

                    # remember the user's email address. this marks the cookie as
                    # authenticated
                    self._transport.factory._cookies[self._transport._cbtid]['authenticated'] = res['email']

                    log.msg("Authenticated user {}".format(res['email']))
                    dres.callback(types.Accept(authid=res['email'], authrole="user", authmethod="mozilla-persona"))
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

    import sys
    import argparse

    from twisted.python import log
    from twisted.internet.endpoints import serverFromString

    # parse command line arguments
    ##
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug output.")

    parser.add_argument("-c", "--component", type=str, default=None,
                        help="Start WAMP-WebSocket server with this application component, e.g. 'timeservice.TimeServiceBackend', or None.")

    parser.add_argument("--websocket", type=str, default="tcp:8080",
                        help='WebSocket server Twisted endpoint descriptor, e.g. "tcp:9000" or "unix:/tmp/mywebsocket".')

    parser.add_argument("--wsurl", type=str, default="ws://localhost:8080",
                        help='WebSocket URL (must suit the endpoint), e.g. "ws://localhost:9000".')

    args = parser.parse_args()

    log.startLogging(sys.stdout)

    # we use an Autobahn utility to install the "best" available Twisted reactor
    ##
    from autobahn.twisted.choosereactor import install_reactor
    reactor = install_reactor()
    if args.debug:
        print("Running on reactor {}".format(reactor))

    # create a WAMP router factory
    ##
    from autobahn.twisted.wamp import RouterFactory
    router_factory = RouterFactory()

    # create a WAMP router session factory
    ##
    from autobahn.twisted.wamp import RouterSessionFactory
    session_factory = RouterSessionFactory(router_factory)
    session_factory.session = MyRouterSession

    # start an embedded application component ..
    ##
    component_config = types.ComponentConfig(realm="realm1")
    component_session = TimeService(component_config)
    session_factory.add(component_session)

    # create a WAMP-over-WebSocket transport server factory
    ##
    from autobahn.twisted.websocket import WampWebSocketServerFactory
    transport_factory = WampWebSocketServerFactory(session_factory, args.wsurl, debug=False, debug_wamp=args.debug)
    transport_factory.protocol = ServerProtocol
    transport_factory._cookies = {}

    transport_factory.setProtocolOptions(failByDrop=False)

    from twisted.web.server import Site
    from twisted.web.static import File
    from autobahn.twisted.resource import WebSocketResource

    # we serve static files under "/" ..
    root = File(".")

    # .. and our WebSocket server under "/ws"
    resource = WebSocketResource(transport_factory)
    root.putChild("ws", resource)

    # run both under one Twisted Web Site
    site = Site(root)

    # start the WebSocket server from an endpoint
    ##
    server = serverFromString(reactor, args.websocket)
    server.listen(site)

    # now enter the Twisted reactor loop
    ##
    reactor.run()
