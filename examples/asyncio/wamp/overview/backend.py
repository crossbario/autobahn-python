from os import environ
import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner


class MyComponent(ApplicationSession):
    @asyncio.coroutine
    def onJoin(self, details):
        # a remote procedure; see frontend.py for a Python front-end
        # that calls this. Any language with WAMP bindings can now call
        # this procedure if its connected to the same router and realm.
        def add2(x, y):
            return x + y
        yield from self.register(add2, u'com.myapp.add2')

        # publish an event every second. The event payloads can be
        # anything JSON- and msgpack- serializable
        while True:
            self.publish(u'com.myapp.hello', 'Hello, world!')
            yield from asyncio.sleep(1)


if __name__ == '__main__':
    runner = ApplicationRunner(
        environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://127.0.0.1:8080/ws"),
        u"crossbardemo",
    )
    runner.run(MyComponent)
