from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks
import os
import argparse
import six

url = os.environ.get('CBURL', u'ws://localhost:8080/ws')
realmv = os.environ.get('CBREALM', u'realm1')
print(url, realmv)
component = Component(transports=url, realm=realmv)


@component.on_join
@inlineCallbacks
def joined(session, details):
    print("session ready")
    counter = 0
    while True:
        # publish() only returns a Deferred if we asked for an acknowledgement
        session.publish(u'com.myapp.hello', "Hello World {0}".format(counter))
        counter += 1
        yield sleep(1)



if __name__ == "__main__":
    run([component])



