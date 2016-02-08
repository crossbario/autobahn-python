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
    parser = argparse.ArgumentParser()

    parser.add_argument("--web", type=int, default=8080,
                        help='Web port to use for embedded Web server. Use 0 to disable.')

    parser.add_argument("--router", type=str, default=None,
                        help='If given, connect to this WAMP router. Else run an embedded router on 9000.')

    args = parser.parse_args()

    from twisted.python import log
    log.startLogging(sys.stdout)

    # import Twisted reactor
    from twisted.internet import reactor
    print("Using Twisted reactor {0}".format(reactor.__class__))

    # create embedded web server for static files
    if args.web:
        from twisted.web.server import Site
        from twisted.web.static import File
        reactor.listenTCP(args.web, Site(File(".")))

    # run WAMP application component
    from autobahn.twisted.wamp import ApplicationRunner
    router = args.router or u'ws://127.0.0.1:9000'

    runner = ApplicationRunner(router, u"realm1", standalone=not args.router)

    # start the component and the Twisted reactor ..
    runner.run(DbusNotifier)
