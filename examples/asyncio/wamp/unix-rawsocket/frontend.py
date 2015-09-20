from __future__ import print_function

try:
    from asyncio import sleep, coroutine, get_event_loop
except ImportError:
    from trollius import sleep, coroutine, get_event_loop

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner, Connection


class ClientSession(ApplicationSession):
    @coroutine
    def onJoin(self, details):
        print("Joined", details)
        sub = yield from self.subscribe(self.subscription, "test.sub")
        print("subscribed", sub)
        print("disconnecting in 5 seconds")
        yield from sleep(5)
        # if you disconnect() then the reconnect logic still keeps
        # trying; if you leave() then it stops trying
        if False:
            print("disconnect()-ing")
            self.disconnect()
        else:
            print("leave()-ing")
            self.leave()

    def onLeave(self, reason):
        self.disconnect()

    def subscription(self, *args, **kw):
        print("sub:", args, kw)


if __name__ == '__main__':
    # we set up a transport that will definitely fail to demonstrate
    # re-connection as well. note that "transports" can be an iterable

    bad_transport = {
        "type": "rawsocket",
        "endpoint": {
            "type": "unix",
            "path": "/tmp/cb-raw-foo",
        }
    }

    websocket_unix_transport = {
        "type": "websocket",
        "url": "ws://127.0.0.1/ws",
        "endpoint": {
            "type": "unix",
            "path": "/tmp/cb-web",
        }
    }

    rawsocket_unix_transport = {
        "type": "rawsocket",
        "url": "ws://127.0.0.1/ws",
        "endpoint": {
            "type": "unix",
            "path": "/tmp/cb-raw",
        }
    }

    retry = dict(
        initial_retry_delay=1,
        retry_growth_rate=2,
        max_retries=2,  # change to 1 for an error
        retry_on_unreachable=True,
    )

    runner = ApplicationRunner([websocket_unix_transport], u"realm1")
    print("calling run", runner, type(runner), runner.run)
    try:
        runner.run(ClientSession)
    except Exception as e:
        print("ERROR", e)
        raise
    print("exiting main")
