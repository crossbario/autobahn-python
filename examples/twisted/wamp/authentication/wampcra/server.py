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

    def add(self, authid, authrole, secret, salt=None):
        if salt:
            key = auth.derive_key(secret.encode('utf8'), salt.encode('utf8')).decode('ascii')
        else:
            key = secret
        self._creds[authid] = (salt, key, authrole)
        return self._creds[authid]

    def get(self, authid):
        # we return a deferred to simulate an asynchronous lookup
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
        self.challenge = json.dumps(challenge_obj, ensure_ascii=False)
        self.signature = auth.compute_wcs(key.encode('utf8'), self.challenge.encode('utf8')).decode('ascii')


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

                    # lookup user in user DB
                    salt, key, role = yield self.factory.userdb.get(details.authid)

                    # if user found ..
                    if key:

                        # setup pending auth
                        self._pending_auth = PendingAuth(key, details.pending_session,
                                                         details.authid, role, authmethod, u"userdb")

                        # send challenge to client
                        extra = {
                            u'challenge': self._pending_auth.challenge
                        }

                        # when using salted passwords, provide the client with
                        # the salt and then PBKDF2 parameters used
                        if salt:
                            extra[u'salt'] = salt
                            extra[u'iterations'] = 1000
                            extra[u'keylen'] = 32

                        defer.returnValue(types.Challenge(u'wampcra', extra))

        # deny client
        defer.returnValue(types.Deny())

    def onAuthenticate(self, signature, extra):
        """
        Callback fired when a client responds to an authentication challenge.
        """
        print("onAuthenticate: {} {}".format(signature, extra))

        # if there is a pending auth, and the signature provided by client matches ..
        if self._pending_auth:

            if signature == self._pending_auth.signature:

                # accept the client
                return types.Accept(authid=self._pending_auth.authid,
                                    authrole=self._pending_auth.authrole,
                                    authmethod=self._pending_auth.authmethod,
                                    authprovider=self._pending_auth.authprovider)
            else:

                # deny client
                return types.Deny(message=u"signature is invalid")
        else:

            # deny client
            return types.Deny(message=u"no pending authentication")


class TimeService(ApplicationSession):

    """
    A simple time service application component.
    """

    def onJoin(self, details):
        print("session attached")

        def utcnow():
            now = datetime.datetime.utcnow()
            return now.strftime(u"%Y-%m-%dT%H:%M:%SZ")

        self.register(utcnow, u'com.timeservice.now')


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

    # create a user DB
    ##
    userdb = UserDb()
    userdb.add(authid=u"peter", authrole=u"user", secret=u"secret1", salt=u"salt123")
    userdb.add(authid=u"joe", authrole=u"user", secret=u"secret2")

    # create a WAMP router session factory
    ##
    from autobahn.twisted.wamp import RouterSessionFactory
    session_factory = RouterSessionFactory(router_factory)
    session_factory.session = MyRouterSession
    session_factory.userdb = userdb

    # start an embedded application component ..
    ##
    component_config = types.ComponentConfig(realm=u"realm1")
    component_session = TimeService(component_config)
    session_factory.add(component_session)

    # create a WAMP-over-WebSocket transport server factory
    ##
    from autobahn.twisted.websocket import WampWebSocketServerFactory
    transport_factory = WampWebSocketServerFactory(session_factory, args.wsurl, debug=False, debug_wamp=args.debug)
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
    site.noisy = False
    site.log = lambda _: None

    # start the WebSocket server from an endpoint
    ##
    server = serverFromString(reactor, args.websocket)
    server.listen(site)

    # now enter the Twisted reactor loop
    ##
    reactor.run()
