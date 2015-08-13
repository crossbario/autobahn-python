from os import environ
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
# or: from autobahn.asyncio.wamp import ApplicationSession

class MyComponent(ApplicationSession):
    @inlineCallbacks
    def onJoin(self, details):
        # listening for the corresponding message from the "backend"
        # (any session that .publish()es to this topic).
        def onevent(msg):
            print("Got event: {}".format(msg))
        yield self.subscribe(onevent, 'com.myapp.hello')

        # call a remote procedure.
        res = yield self.call('com.myapp.add2', 2, 3)
        print("Got result: {}".format(res))


if __name__ == '__main__':
    runner = ApplicationRunner(
        environ.get("AUTOBAHN_DEMO_ROUTER", "ws://127.0.0.1:8080/ws"),
        u"crossbardemo",
        debug_wamp=False,  # optional; log many WAMP details
        debug=False,  # optional; log even more details
    )
    runner.run(MyComponent)
