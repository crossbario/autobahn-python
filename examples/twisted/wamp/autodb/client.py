#!/usr/bin/env python
###############################################################################
##
##  Copyright (C) 2014 Greg Fausak
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

import sys,os,argparse,six,json

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationRunner

from autobahn import util
from autobahn.wamp import auth
from autobahn.twisted.wamp import ApplicationSession

import postgres

args = {}

class Component(ApplicationSession):
    """
    An application component demonstrating database action
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
        print("Component:onJoin details: {}").format(details)
        # yield self.call('adm.db.start', 'PG9_4', 'com.db')
        # this client assumes that a database was already installed at com.db, otherwise, we would need to install it ourselves.

        #try:
        #    yield self.call('com.db.connect', 'dbname=autobahn host=localhost user=autouser')
        #except Exception as err:
        #    print("Query connect(ERROR) : {}").format(err)
        #    # we need to raise the error to exit here, connection didn't work, so
        #    # no need to try the queries
        #    raise err

        print("Component:onJoin connect done")

        try:
            rv = yield self.call('com.db.operation', """
                insert into
                    login
                        (password, fullname, login)
                    values
                        (%(password)s,%(fullname)s,%(login)s)""",
                    {
                        'password':'testpass',
                        'fullname':'Test User',
                        'login':'testuser'
                    })
        except Exception as err:
            print("Operation result(ERROR) : {}").format(err)
        else:
            print("Operation result(SUCCESS)")

        try:
            rv = yield self.call('com.db.query', 'select * from login', None)
        except Exception as err:
            print("Query result(ERROR) : {}").format(err)
        else:
            print("Query result(SUCCESS) : {}").format(json.dumps(rv,indent=4))

        #yield self.call('com.db.disconnect')

        print("Component:onJoin done here")
        self.leave()

    def onLeave(self, details):
        print("onLeave: {}").format(details)
        self.disconnect()

    @inlineCallbacks
    def onDisconnect(self):
        print("onDisconnect:")
        reactor.stop()


if __name__ == '__main__':
    prog = os.path.basename(__file__)

    def_wsocket = 'ws://127.0.0.1:8080/ws'
    def_user = 'db'
    def_secret = 'dbsecret'
    def_realm = 'realm1'

    p = argparse.ArgumentParser(description="db client example for autobahn")

    p.add_argument('-w', '--websocket', action='store', dest='wsocket', default=def_wsocket,
                        help='web socket '+def_wsocket)
    p.add_argument('-r', '--realm', action='store', dest='realm', default=def_realm,
                        help='connect to websocket using "realm" '+def_realm)
    p.add_argument('-u', '--user', action='store', dest='user', default=def_user,
                        help='connect to websocket as "user" '+def_user)
    p.add_argument('-s', '--secret', action='store', dest='password', default=def_secret,
                        help='users "secret" password'+def_secret)

    args = p.parse_args()

    args = p.parse_args()

    runner = ApplicationRunner(args.wsocket, args.realm)
    runner.run(Component)
