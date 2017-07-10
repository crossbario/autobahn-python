

from autobahn.asyncio.component import Component, run
from autobahn.wamp.types import RegisterOptions

import asyncio
import ssl


context = ssl.create_default_context(
    purpose=ssl.Purpose.SERVER_AUTH,
    cafile='../../../router/.crossbar/server.crt',
)
component = Component(
    transports=[
        {
            "type": "websocket",
            "url": u"wss://localhost:8083/ws",
            "endpoint": {
                "type": "tcp",
                "host": "localhost",
                "port": 8083,
                "tls": context,
            },
            "options": {
                "open_handshake_timeout": 100,
            }
        },
    ],
    realm=u"crossbardemo",
)


@component.on_join
def join(session, details):
    print("joined {}".format(details))


@component.register(
    u"example.foo",
    options=RegisterOptions(details_arg='details'),
)
@asyncio.coroutine
def foo(*args, **kw):
    print("foo({}, {})".format(args, kw))
    for x in range(5, 0, -1):
        print("  returning in {}".format(x))
        yield from asyncio.sleep(1)
    print("returning '42'")
    return 42


if __name__ == "__main__":
    run([component])
