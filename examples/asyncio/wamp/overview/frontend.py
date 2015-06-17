from os import environ
import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

class MyComponent(ApplicationSession):
    @asyncio.coroutine
    def onJoin(self, details):
        # listening for the corresponding message from the "backend"
        # (any session that .publish()es to this topic).
        def onevent(msg):
            print("Got event: {}".format(msg))
        yield from self.subscribe(onevent, 'com.myapp.hello')

        # call a remote procedure.
        res = yield from self.call('com.myapp.add2', 2, 3)
        print("Got result: {}".format(res))


if __name__ == '__main__':
    runner = ApplicationRunner(
        environ.get("AUTOBAHN_DEMO_ROUTER", "ws://localhost:8080/ws"),
        u"crossbardemo",
        debug_wamp=False,  # optional; log many WAMP details
        debug=False,  # optional; log even more details
    )
    runner.run(MyComponent)
