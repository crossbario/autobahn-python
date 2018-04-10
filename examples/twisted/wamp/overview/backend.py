from os import environ
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
# or: from autobahn.asyncio.wamp import ApplicationSession


class Component(ApplicationSession):
    @inlineCallbacks
    def onJoin(self, details):
        # publish an event every second. The event payloads can be
        # anything JSON- and msgpack- serializable
        def publish():
            return self.publish(u'com.myapp.hello', 'Hello, world!')
        LoopingCall(publish).start(1)

        # a remote procedure; see frontend.py for a Python front-end
        # that calls this. Any language with WAMP bindings can now call
        # this procedure if its connected to the same router and realm.
        def add2(x, y):
            return x + y
        yield self.register(add2, u'com.myapp.add2')


if __name__ == '__main__':
    import six
    url = environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://127.0.0.1:8080/ws")
    if six.PY2 and type(url) == six.binary_type:
        url = url.decode('utf8')
    realm = u"crossbardemo"
    runner = ApplicationRunner(url, realm)
    runner.run(Component)
