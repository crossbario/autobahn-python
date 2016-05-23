import asyncio
import sys
import logging
import os.path
log = logging.getLogger('frontend')

sys.path = [os.path.join(os.path.dirname(__file__), '../../../..')]+sys.path

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunnerRawSocket
from autobahn.wamp import ApplicationError


class MyComponent(ApplicationSession):
    @asyncio.coroutine
    def onJoin(self, details):
        # listening for the corresponding message from the "backend"
        # (any session that .publish()es to this topic).
        def onevent(msg):
            log.info("Got event: {}".format(msg))
        yield from self.subscribe(onevent, u'com.myapp.hello')

        # call a remote procedure.
        count = 0
        while True:
            try:
                res = yield from self.call(u'com.myapp.add2', count, count+1)
                log.info("Got result: {}".format(res))
            except ApplicationError:
                pass
            count += 1

            yield from asyncio.sleep(2)


if __name__ == '__main__':
    level = 'info'
    if len(sys.argv) > 1 and sys.argv[1] == ' debug':
        level = 'debug'
    runner = ApplicationRunnerRawSocket(
        "tcp://localhost:9090",
        u"realm1")
    runner.run(MyComponent, logging_level=level)
