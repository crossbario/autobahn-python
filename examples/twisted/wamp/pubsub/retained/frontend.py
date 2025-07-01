###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
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

from os import environ

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationRunner, Session
from autobahn.wamp.types import SubscribeOptions
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks


class Component(Session):
    """
    An application component calling the different backend procedures.
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("session attached {}".format(details))

        def got_event(*args, **kw):
            print("got_event(): args={}, kwargs={}".format(args, kw))

        # note: we're relying on 'com.example.history' (the one with
        # event-history enabled) being last so that "pub" has the
        # right ID for wamp.subscription.get_events after the loop
        for topic in ["com.example.no_history_here", "com.example.history"]:
            print("subscribing to '{}'".format(topic))
            pub = yield self.subscribe(
                got_event,
                topic,
                options=SubscribeOptions(get_retained=True),
            )
            print("id={}".format(pub.id))

        events = yield self.call("wamp.subscription.get_events", pub.id)
        print("Using the WAMP Meta API:")
        print("wamp.subscription.get_events {}: {}".format(pub.id, len(events)))
        for event in events:
            print(
                "  {event[timestamp]} {event[topic]} args={event[args]} kwargs={event[kwargs]}".format(
                    event=event
                )
            )


if __name__ == "__main__":
    runner = ApplicationRunner(
        environ.get("AUTOBAHN_DEMO_ROUTER", "ws://127.0.0.1:8080/auth_ws"),
        "crossbardemo",
    )
    runner.run(Component)
