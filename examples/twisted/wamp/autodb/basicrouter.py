###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##        http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import json
import six

from twisted.internet.defer import inlineCallbacks

from autobahn import util
from autobahn.wamp import auth
from autobahn.wamp import types
from autobahn.wamp.interfaces import IRouter
from autobahn.twisted.wamp import Router
from autobahn.twisted.wamp import RouterSession
from twisted.internet import defer
from autobahn.twisted.wamp import ApplicationSession

import postgres

#
# this is the database controller which is connected to the router
#
class ROUTERDB(ApplicationSession):
    """
    An application component providing db access
    """
    def __init__(self, c, rd):
        print("ROUTERDB:__init__")
        ApplicationSession.__init__(self,c)
        self.routerdb = rd
        # we give the routerdb a hook so it can publish add/delete, rpc
        rd.app_session = self
        return

    def onConnect(self):
        print("ROUTERDB:onConnect")
        self.join(self.config.realm, [u"wampcra"], u'routerdb')

#    def onChallenge(self, challenge):
#        print("ROUTERDB:onChallenge")
#        print challenge
#
    @inlineCallbacks
    def onJoin(self, details):
        print("db:onJoin session attached")

        # load the database module and register connect,disconnect,query
        @inlineCallbacks
        def dbstart(dbtype,dbtopicroot):
            print("DB:dbstart: dbtype: {} dbtopicroot: {}").format(dbtype,dbtopicroot)
            if not hasattr(self,'db'):
                self.db = {}
            if dbtopicroot in self.db:
                raise Exception("dbtopicroot already running")
            if dbtype == 'PG9_4':
                dbo = postgres.PG9_4(self)
            else:
                raise Exception("Unsupported dbtype {} ".format(dbtype))
            self.db[dbtopicroot] = { 'instance': dbo }
            self.db[dbtopicroot]['registration'] = {}

            self.db[dbtopicroot]['registration']['connect'] = yield self.register(dbo.connect, dbtopicroot+'.connect')
            self.db[dbtopicroot]['registration']['disconnect'] = yield self.register(dbo.disconnect, dbtopicroot+'.disconnect')
            self.db[dbtopicroot]['registration']['query'] = yield self.register(dbo.query, dbtopicroot+'.query')
            self.db[dbtopicroot]['registration']['operation'] = yield self.register(dbo.operation, dbtopicroot+'.operation')

            return

        @inlineCallbacks
        def dbstop(dbtopicroot):
            print("DB:dbstop: {}").format(dbtopicroot)

            yield self.db[dbtopicroot]['registration']['connect'].unregister()
            yield self.db[dbtopicroot]['registration']['disconnect'].unregister()
            yield self.db[dbtopicroot]['registration']['query'].unregister()
            yield self.db[dbtopicroot]['registration']['operation'].unregister()

            del self.db[dbtopicroot]
            return

        yield self.register(dbstart, u'adm.db.start')
        yield self.register(dbstop, u'adm.db.stop')
        print("db bootstrap procedures registered")

        # this is our database for authentication and authorization
        yield self.call('adm.db.start', 'PG9_4', 'com.db')
        print("postgres 9.4 database attached")
        yield self.call('com.db.connect', 'dbname=autobahn host=localhost user=autouser')
        print("administration connection established")


    def onLeave(self, details):
        print("onLeave: {}").format(details)

    def onDisconnect(self):
        print("onDisconnect:")

class SessionData(ApplicationSession):
    def __init__(self, c, sd):
        print("SessionData:__init__")
        ApplicationSession.__init__(self,c)
        self.sessiondb = sd
        # we give the sessiondb a hook so it can publish add/delete
        sd.app_session = self
        return

    def onConnect(self):
        print("SessionData:onConnect")
        self.join(self.config.realm, [u"wampcra"], u'sessiondata')

    def onChallenge(self, challenge):
        print("SessionData:onChallenge")
        print challenge

    @inlineCallbacks
    def onJoin(self, details):
        print("onJoin: {}").format(details)

        def list_data():
            print("SessionData:list_data()")
            return self.sessiondb.list()

        def kill_session(sid):
            print("SessionData:kill_session({})").format(sid)
            ses = self.sessiondb.get(sid)
            ses._transport.sendClose(code=3000,reason=six.u('killed'))
            return defer.succeed({ 'killed': sid })

        reg = yield self.register(list_data, 'adm.session.list')
        reg = yield self.register(kill_session, 'adm.session.kill')

    def onLeave(self, details):
        print("onLeave: {}".format(details))

    def onDisconnect(self):
        print("disconnected")


class MyRouter(Router):

    def authorize(self, session, uri, action):
        print("MyRouter.authorize: {} {} {} {}".format(session._authid, session._session_id, uri, IRouter.ACTION_TO_STRING[action]))

        return True

    def validate(self, payload_type, uri, args, kwargs):
        print("MyRouter.validate: {}").format(payload_type)

        return True


class UserDb:
    """
    A fake user database.
    """

    def __init__(self):
        self._creds = {}
        # this gets set by the ROUTERDB
        self.app_session = None

    @inlineCallbacks
    def get(self, authid):
        rv = yield self.app_session.call('com.db.query', "select password from login where login = %(login)s",
                { 'login':authid })
        if len(rv) > 0:
            defer.returnValue((None, six.u(rv[0]['password']), six.u('user')))
        else:
            defer.returnValue((None, None, None))

        return
        # we return a deferred to simulate an asynchronous lookup
        # return defer.succeed(self._creds.get(authid, (None, None, None)))

class SessionDb:
    """
    A session database.
    """

    def __init__(self):
        self._sessiondb = {}
        self.app_session = None

    def add(self, sessionid, session_body):
        print("SessionDb.add({})").format(sessionid)
        self._sessiondb[sessionid] = session_body
        if self.app_session is not None:
            self.app_session.publish('com.client.add',sessionid)
        return

    def get(self, sessionid):
        print("SessionDb.get({})").format(sessionid)
        ## we return a deferred to simulate an asynchronous lookup
        return self._sessiondb.get(sessionid, {})

    def list(self):
        print("SessionDb.list()")
        ## we return a deferred to simulate an asynchronous lookup
        rv = {}
        for k in self._sessiondb:
            print("SessionDb.list:key({})").format(k)
            #print dir(self._sessiondb[k])
            sib = self._sessiondb[k]
            rv[k] = { 'session_id':k, 'id': sib._authid, 'provider': sib._authprovider, 'role': sib._authrole  }

        return defer.succeed(rv)

    def delete(self, sessionid):
        print("SessionDb.delete({})").format(sessionid)
        if self.app_session is not None:
            self.app_session.publish('com.client.delete',sessionid)
        ## we return a deferred to simulate an asynchronous lookup
        try:
            del self._sessiondb[sessionid]
        except:
            pass
        return

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
        self.challenge = json.dumps(challenge_obj, ensure_ascii = False)
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

                    ## lookup user in user DB
                    salt, key, role = yield self.factory.userdb.get(details.authid)
                    print("salt, key, role: {} {} {}".format(salt, key, role))

                    ## if user found ..
                    if key:

                        ## setup pending auth
                        self._pending_auth = PendingAuth(key, details.pending_session,
                            details.authid, role, authmethod, u"userdb")

                        ## send challenge to client
                        extra = {
                            u'challenge': self._pending_auth.challenge
                        }

                        ## when using salted passwords, provide the client with
                        ## the salt and then PBKDF2 parameters used
                        if salt:
                            extra[u'salt'] = salt
                            extra[u'iterations'] = 1000
                            extra[u'keylen'] = 32

                        defer.returnValue(types.Challenge(u'wampcra', extra))

        ## deny client
        defer.returnValue(types.Deny())


    def onAuthenticate(self, signature, extra):
        """
        Callback fired when a client responds to an authentication challenge.
        """
        print("onAuthenticate: {} {}".format(signature, extra))

        ## if there is a pending auth, and the signature provided by client matches ..
        if self._pending_auth:

            if signature == self._pending_auth.signature:

                ## accept the client
                return types.Accept(authid = self._pending_auth.authid,
                    authrole = self._pending_auth.authrole,
                    authmethod = self._pending_auth.authmethod,
                    authprovider = self._pending_auth.authprovider)
            else:

                ## deny client
                return types.Deny(message = u"signature is invalid")
        else:

            ## deny client
            return types.Deny(message = u"no pending authentication")

    def onJoin(self, details):
        print("MyRouterSession.onJoin: {}").format(details)
        self.factory.sessiondb.add(details.session, self)
        return

    def onLeave(self, details):
        print("onLeave: {}").format(details)
        self.factory.sessiondb.delete(self._session_id)
        return

    def onDisconnect(self, details):
        print("onDisconnect: {}").format(details)
        return


if __name__ == '__main__':

    import sys, argparse

    from twisted.python import log
    from twisted.internet.endpoints import serverFromString

    ## parse command line arguments
    ##
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", action = "store_true",
                              help = "Enable debug output.")

    parser.add_argument("--endpoint", type = str, default = "tcp:8080",
                              help = 'Twisted server endpoint descriptor, e.g. "tcp:8080" or "unix:/tmp/mywebsocket".')

    args = parser.parse_args()
    log.startLogging(sys.stdout)

    ## we use an Autobahn utility to install the "best" available Twisted reactor
    ##
    from autobahn.twisted.choosereactor import install_reactor
    reactor = install_reactor()
    print("Running on reactor {}".format(reactor))

    ## create a user DB
    ##
    userdb = UserDb()
    sessiondb = SessionDb()

    ## create a WAMP router factory
    ##
    from autobahn.twisted.wamp import RouterFactory
    router_factory = RouterFactory()
    router_factory.router = MyRouter


    ## create a WAMP router session factory
    ##
    from autobahn.twisted.wamp import RouterSessionFactory
    session_factory = RouterSessionFactory(router_factory)
    session_factory.session = MyRouterSession
    session_factory.userdb = userdb
    session_factory.sessiondb = sessiondb

    component_config = types.ComponentConfig(realm = "realm1")
    component_session = SessionData(component_config,sessiondb)
    session_factory.add(component_session)

    db_session = ROUTERDB(component_config,userdb)
    session_factory.add(db_session)

    ## create a WAMP-over-WebSocket transport server factory
    ##
    from autobahn.twisted.websocket import WampWebSocketServerFactory
    transport_factory = WampWebSocketServerFactory(session_factory, debug = args.debug)
    transport_factory.setProtocolOptions(failByDrop = False)


    ## start the server from an endpoint
    ##
    server = serverFromString(reactor, args.endpoint)
    server.listen(transport_factory)


    ## now enter the Twisted reactor loop
    ##
    reactor.run()
