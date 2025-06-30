import asyncio
import logging
import os.path
import sys
from datetime import datetime

log = logging.getLogger("backend")

sys.path = [os.path.join(os.path.dirname(__file__), "../../../..")] + sys.path

from runner import ApplicationRunnerRawSocket

from autobahn.asyncio.wamp import ApplicationSession


class MyComponent(ApplicationSession):
    async def onJoin(self, details):
        # a remote procedure; see frontend.py for a Python front-end
        # that calls this. Any language with WAMP bindings can now call
        # this procedure if its connected to the same router and realm.
        def add2(x, y):
            log.debug("add2 called with %s %s", x, y)
            return x + y

        await self.register(add2, "com.myapp.add2")

        # publish an event every second. The event payloads can be
        # anything JSON- and msgpack- serializable
        while True:
            self.publish(
                "com.myapp.hello", "Hello, world! Time is %s" % datetime.utcnow()
            )
            log.debug("Published msg")
            await asyncio.sleep(1)


if __name__ == "__main__":
    level = "info"
    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        level = "debug"
    path = os.path.join(os.path.dirname(__file__), ".crossbar/socket1")
    runner = ApplicationRunnerRawSocket(
        path,
        "realm1",
    )
    runner.run(MyComponent, logging_level=level)
