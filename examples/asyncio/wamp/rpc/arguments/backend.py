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

try:
    import asyncio
except ImportError:
    # Trollius >= 0.3 was renamed
    import trollius as asyncio

from os import environ
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner


class Component(ApplicationSession):
    """
    An application component providing procedures with different kinds
    of arguments.
    """

    @asyncio.coroutine
    def onJoin(self, details):

        def ping():
            return

        def add2(a, b):
            return a + b

        def stars(nick="somebody", stars=0):
            return u"{} starred {}x".format(nick, stars)

        # noinspection PyUnusedLocal
        def orders(product, limit=5):
            return [u"Product {}".format(i) for i in range(50)][:limit]

        def arglen(*args, **kwargs):
            return [len(args), len(kwargs)]

        yield from self.register(ping, u'com.arguments.ping')
        yield from self.register(add2, u'com.arguments.add2')
        yield from self.register(stars, u'com.arguments.stars')
        yield from self.register(orders, u'com.arguments.orders')
        yield from self.register(arglen, u'com.arguments.arglen')
        print("Registered methods; ready for frontend.")


if __name__ == '__main__':
    runner = ApplicationRunner(
        environ.get("AUTOBAHN_DEMO_ROUTER", "ws://127.0.0.1:8080/ws"),
        u"crossbardemo",
        debug_wamp=False,  # optional; log many WAMP details
        debug=False,  # optional; log even more details
    )
    runner.run(Component)
