import os
from random import randint

import txaio
txaio.use_twisted()

from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from autobahn.util import hltype, hlval
from autobahn.twisted.component import Component, run
from autobahn.wamp.types import PublishOptions
from autobahn.wamp.exception import ApplicationError

log = txaio.make_logger()


@inlineCallbacks
def main(reactor, session):
    log.info('{func} session connected.\nsession_details=\n{session_details}\transport_details={transport_details}',
             session_details=session.session_details,
             transport_details=session.transport.transport_details,
             func=hltype(main))
    while session.is_attached():
        x = randint(0, 2**16)
        y = randint(0, 2**16)
        s = yield session.call('user.add2', x, y)
        assert s == x + y
        sq = s * s
        pub = yield session.publish('user.on_square', sq, options=PublishOptions(acknowledge=True))
        log.info('{func} published event {pub_id}: sq={sq}',
                 func=hltype(main),
                 sq=hlval(sq),
                 pub_id=hlval(pub.id))
        yield sleep(1)


if __name__ == "__main__":
    # transports = os.environ.get('WAMP_ROUTER_URLS', '').split(',')
    transports = ['ws://localhost:8080/ws', 'ws://localhost:8081/ws', 'ws://localhost:8082/ws']
    # transports = ['ws://localhost:8080/ws']
    realm = 'realm1'
    authentication = {
        'cryptosign': {
            'privkey': '20e8c05d0ede9506462bb049c4843032b18e8e75b314583d0c8d8a4942f9be40',
        }
    }

    component = Component(transports=transports,
                          main=main,
                          realm=realm,
                          authentication=authentication)
    run([component])
