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

import sys
import json
import urllib
import Cookie

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

import autobahn
from autobahn.util import newid, utcnow
from autobahn.websocket import http

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol

from autobahn.twisted.resource import WebSocketResource


class PersonaServerProtocol(WebSocketServerProtocol):

    """
    WebSocket server protocol that tracks WebSocket connections using HTTP cookies,
    and authenticates WebSocket connections using Mozilla Persona.
    """

    def onConnect(self, request):

        # This is called during the initial WebSocket opening handshake.

        protocol, headers = None, {}

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

        # accept the WebSocket connection, speaking subprotocol `protocol`
        # and setting HTTP headers `headers`
        return (protocol, headers)

    def onOpen(self):

        # This is called when initial WebSocket opening handshake has
        # been completed.

        # see if we are authenticated ..
        authenticated = self.factory._cookies[self._cbtid]['authenticated']

        if not authenticated:
            # .. if not, send authentication request
            self.sendMessage(json.dumps({'cmd': 'AUTHENTICATION_REQUIRED'}))
        else:
            # .. if yes, send info on authenticated user
            self.sendMessage(json.dumps({'cmd': 'AUTHENTICATED', 'email': authenticated}))

    def onClose(self, wasClean, code, reason):

        # This is called when WebSocket connection is gone

        # remove this connection from list of connections associated with
        # same cookie
        self.factory._cookies[self._cbtid]['connections'].remove(self)

        # if list gets empty, possibly do something ..
        if not self.factory._cookies[self._cbtid]['connections']:
            log.msg("All connections for {} gone".format(self._cbtid))

    def onMessage(self, payload, isBinary):

        # This is called when we receive a WebSocket message

        if not isBinary:

            msg = json.loads(payload)

            if msg['cmd'] == 'AUTHENTICATE':

                # The client did it's Mozilla Persona authentication thing
                # and now wants to verify the authentication and login.
                assertion = msg.get('assertion')
                audience = msg.get('audience')

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
                    if res['status'] == 'okay':
                        # Mozilla Persona successfully authenticated the user

                        # remember the user's email address. this marks the cookie as
                        # authenticated
                        self.factory._cookies[self._cbtid]['authenticated'] = res['email']

                        # inform _all_ WebSocket connections of the successful auth.
                        msg = json.dumps({'cmd': 'AUTHENTICATED', 'email': res['email']})
                        for proto in self.factory._cookies[self._cbtid]['connections']:
                            proto.sendMessage(msg)

                        log.msg("Authenticated user {}".format(res['email']))
                    else:
                        log.msg("Authentication failed: {}".format(res.get('reason')))
                        self.sendMessage(json.dumps({'cmd': 'AUTHENTICATION_FAILED', 'reason': res.get('reason')}))
                        self.sendClose()

                def error(err):
                    log.msg("Authentication request failed: {}".format(err.value))
                    self.sendMessage(json.dumps({'cmd': 'AUTHENTICATION_FAILED', 'reason': str(err.value)}))
                    self.sendClose()

                d.addCallbacks(done, error)

            elif msg['cmd'] == 'LOGOUT':

                # user wants to logout ..
                if self.factory._cookies[self._cbtid]['authenticated']:
                    self.factory._cookies[self._cbtid]['authenticated'] = False

                    # inform _all_ WebSocket connections of the logout
                    msg = json.dumps({'cmd': 'LOGGED_OUT'})
                    for proto in self.factory._cookies[self._cbtid]['connections']:
                        proto.sendMessage(msg)

            else:
                log.msg("unknown command {}".format(msg))


class PersonaServerFactory(WebSocketServerFactory):

    """
    WebSocket server factory with cookie/sessions map.
    """

    protocol = PersonaServerProtocol

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url, debug=False)

        # map of cookies
        self._cookies = {}


if __name__ == '__main__':

    log.startLogging(sys.stdout)

    print("Running Autobahn|Python {}".format(autobahn.version))

    # our WebSocket server factory
    factory = PersonaServerFactory(u"ws://127.0.0.1:8080")

    # we serve static files under "/" ..
    root = File(".")

    # .. and our WebSocket server under "/ws"
    resource = WebSocketResource(factory)
    root.putChild(u"ws", resource)

    # run both under one Twisted Web Site
    site = Site(root)
    site.log = lambda _: None  # disable any logging

    reactor.listenTCP(8080, site)

    reactor.run()
