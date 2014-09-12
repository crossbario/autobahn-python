#!/usr/bin/env python
###############################################################################
##
##  Copyright (C) 2014 Greg Fausak
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

import sys,os,argparse,six

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationRunner

from autobahn import util
from autobahn.wamp import auth
from autobahn.twisted.wamp import ApplicationSession

import postgres

args = {}

class DB(ApplicationSession):
    """
    An application component providing db access
    """

    def onConnect(self):
        self.join(self.config.realm, [u'wampcra'], six.u(args.user))

    def onChallenge(self, challenge):
        print challenge
        if challenge.method == u'wampcra':
            if u'salt' in challenge.extra:
                key = auth.derive_key(args.password.encode('utf8'),
                    challenge.extra['salt'].encode('utf8'),
                    challenge.extra.get('iterations', None),
                    challenge.extra.get('keylen', None))
            else:
                key = args.password.encode('utf8')
            signature = auth.compute_wcs(key, challenge.extra['challenge'].encode('utf8'))
            return signature.decode('ascii')
        else:
            raise Exception("don't know how to compute challenge for authmethod {}".format(challenge.method))

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

        def query(q):
            print("DB:query: {}").format(q)
            return

        yield self.register(dbstart, u'adm.db.start')
        yield self.register(dbstop, u'adm.db.stop')
        if args.engine is not None:
            print("db:onJoin engine {} and topic base {} activation").format(args.engine, args.topic_base)
            yield self.call('adm.db.start', args.engine, args.topic_base)

        print("db bootstrap procedures registered")

    def onLeave(self, details):
        print("onLeave: {}").format(details)
        self.disconnect()

    def onDisconnect(self):
        print("onDisconnect:")
        reactor.stop()


if __name__ == '__main__':
    prog = os.path.basename(__file__)

    def_wsocket = 'ws://127.0.0.1:8080/ws'
    def_user = 'db'
    def_secret = 'dbsecret'
    def_realm = 'realm1'
    def_topic_base = 'com.db'

    p = argparse.ArgumentParser(description="db admin manager for autobahn")

    p.add_argument('-w', '--websocket', action='store', dest='wsocket', default=def_wsocket,
                        help='web socket '+def_wsocket)
    p.add_argument('-r', '--realm', action='store', dest='realm', default=def_realm,
                        help='connect to websocket using "realm" '+def_realm)
    p.add_argument('-u', '--user', action='store', dest='user', default=def_user,
                        help='connect to websocket as "user" '+def_user)
    p.add_argument('-s', '--secret', action='store', dest='password', default=def_secret,
                        help='users "secret" password')
    p.add_argument('-e', '--engine', action='store', dest='engine', default=None,
                        help='if specified, a database engine will be attached. Note engine is rooted on --topic')
    p.add_argument('-t', '--topic', action='store', dest='topic_base', default=def_topic_base,
                        help='if you specify --dsn then you will need a topic to root it on, the default ' + def_topic_base + ' is fine.')

    args = p.parse_args()

    runner = ApplicationRunner(args.wsocket, args.realm)
    runner.run(DB)
