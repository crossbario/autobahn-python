from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks
import os
import argparse
import six
import datetime

url = os.environ.get('CBURL', u'ws://localhost:8080/ws')
realmv = os.environ.get('CBREALM', u'realm1')
print(url, realmv)
component = Component(transports=url, realm=realmv)


@component.on_join
@inlineCallbacks
def joined(session, details):
    print("session ready")
    try:
        res = yield session.call(u'com.myapp.date')
        print("\ncall result: {}\n".format(res))
    except Exception as e:
        print("call error: {0}".format(e))
    yield session.leave()


if __name__ == "__main__":
    run([component])



