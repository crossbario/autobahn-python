from os import environ

from autobahn.twisted.wamp import ApplicationRunner, ApplicationSession
from twisted.internet.defer import inlineCallbacks

# or: from autobahn.asyncio.wamp import ApplicationSession


class Component(ApplicationSession):
    @inlineCallbacks
    def onJoin(self, details):
        # listening for the corresponding message from the "backend"
        # (any session that .publish()es to this topic).
        def onevent(msg):
            print("Got event: {}".format(msg))

        yield self.subscribe(onevent, "com.myapp.hello")

        # call a remote procedure.
        res = yield self.call("com.myapp.add2", 2, 3)
        print("Got result: {}".format(res))


if __name__ == "__main__":
    url = environ.get("AUTOBAHN_DEMO_ROUTER", "ws://127.0.0.1:8080/ws")
    realm = "crossbardemo"
    runner = ApplicationRunner(url, realm)
    runner.run(Component)
