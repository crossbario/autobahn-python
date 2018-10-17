from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from twisted.internet.defer import inlineCallbacks
import os

url = os.environ.get('CBURL', u'ws://localhost:8080/ws')
realmvalue = os.environ.get('CBREALM', u'realm1')
component = Component(transports=url, realm=realmvalue)


@component.on_join
@inlineCallbacks
def joined(session, details):
    print("session ready")

    def oncounter(count):
        print("event received: {0}", count)

    try:
        yield session.subscribe(oncounter, u'com.myapp.hello')
        print("subscribed to topic")
    except Exception as e:
        print("could not subscribe to topic: {0}".format(e))


if __name__ == "__main__":
    run([component])



