import asyncio
import sys
import logging
import os.path

log = logging.getLogger("frontend")

sys.path = [os.path.join(os.path.dirname(__file__), "../../../..")] + sys.path

from autobahn.asyncio.wamp import ApplicationSession
from runner import ApplicationRunnerRawSocket
from autobahn.wamp import ApplicationError


class MyComponent(ApplicationSession):
    async def onJoin(self, details):
        # listening for the corresponding message from the "backend"
        # (any session that .publish()es to this topic).
        def onevent(msg):
            log.info("Got event: {}".format(msg))

        await self.subscribe(onevent, "com.myapp.hello")

        # call a remote procedure.
        count = 0
        while True:
            try:
                res = await self.call("com.myapp.add2", count, count + 1)
                log.info("Got result: {}".format(res))
            except ApplicationError:
                pass
            count += 1

            await asyncio.sleep(2)


if __name__ == "__main__":
    level = "info"
    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        level = "debug"
    runner = ApplicationRunnerRawSocket("tcp://localhost:9090", "realm1")
    runner.run(MyComponent, logging_level=level)
