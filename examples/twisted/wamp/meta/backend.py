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
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks


class Component(Session):
    """
    An application component calling the different backend procedures.
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("session attached {}".format(details))
        counter = 0
        while True:
            counter += 1

            pub = yield self.publish("event.foo.{}".format(counter), "some data")
            print("published {}".format(pub))
            yield sleep(1)

            sub = yield self.subscribe(lambda: None, "event.sub_{}".format(counter))
            print("subscribed {sub.id}".format(sub=sub))
            yield sleep(1)

            reg = yield self.register(lambda: 42, "event.rpc.test_{}".format(counter))
            print("registered {reg.id}".format(reg=reg))
            yield sleep(1)

            call = yield self.call("event.rpc.test_{}".format(counter))
            print("called {}".format(call))
            yield sleep(1)

            yield reg.unregister()
            yield sub.unsubscribe()


if __name__ == "__main__":
    runner = ApplicationRunner(
        environ.get("AUTOBAHN_DEMO_ROUTER", "ws://127.0.0.1:8080/auth_ws"),
        "crossbardemo",
    )
    runner.run(Component)
