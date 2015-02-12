###############################################################################
##
# Copyright (C) 2012-2014 Tavendo GmbH
##
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
##
# http://www.apache.org/licenses/LICENSE-2.0
##
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##
###############################################################################

from twisted.internet.defer import inlineCallbacks

from txdbus import error, client

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.util import sleep


class DbusNotifier(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):

        conn = yield client.connect(reactor, 'session')
        print("Dbus connection created")

        self._notifier = yield conn.getRemoteObject('org.freedesktop.Notifications',
                                                    '/org/freedesktop/Notifications')
        print("Dbus notification object created")

        yield self.subscribe(self)
        print("Dbus notifier subscribed")

    @inlineCallbacks
    @wamp.subscribe(u'com.example.dbus.on_notify')
    def onNotify(self, title, body, duration=2):

        print("Notification received: title = '{}', body = '{}', duration = {}".format(title, body, duration))

        try:
            nid = yield self._notifier.callRemote('Notify',
                                                  'WAMP/Dbus Notifier',
                                                  0,
                                                  '',
                                                  str(title),
                                                  str(body),
                                                  [],
                                                  {},
                                                  1)

            print("Desktop notification shown (NID = {}).. closing in {} seconds".format(nid, duration))

            yield sleep(duration)
            print("Closing notification")

            yield self._notifier.callRemote('CloseNotification', nid)
            print("Notification closed")

        except Exception as e:
            print("ERROR: {}".format(e))


if __name__ == '__main__':

    import sys
    import argparse

    # parse command line arguments
    ##
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug output.")

    parser.add_argument("--web", type=int, default=8080,
                        help='Web port to use for embedded Web server. Use 0 to disable.')

    parser.add_argument("--router", type=str, default=None,
                        help='If given, connect to this WAMP router. Else run an embedded router on 9000.')

    args = parser.parse_args()

    if args.debug:
        from twisted.python import log
        log.startLogging(sys.stdout)

    # import Twisted reactor
    ##
    from twisted.internet import reactor
    print("Using Twisted reactor {0}".format(reactor.__class__))

    # create embedded web server for static files
    ##
    if args.web:
        from twisted.web.server import Site
        from twisted.web.static import File
        reactor.listenTCP(args.web, Site(File(".")))

    # run WAMP application component
    ##
    from autobahn.twisted.wamp import ApplicationRunner
    router = args.router or 'ws://localhost:9000'

    runner = ApplicationRunner(router, u"realm1", standalone=not args.router,
                               debug=False,             # low-level logging
                               debug_wamp=args.debug,   # WAMP level logging
                               debug_app=args.debug     # app-level logging
                               )

    # start the component and the Twisted reactor ..
    ##
    runner.run(DbusNotifier)
