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


#@component.register
#def utcnow():
#    now = datetime.datetime.utcnow()
#    return now.strftime("%Y-%m-%dT%H:%M:%SZ")

@component.on_join
@inlineCallbacks
def joined(session, details):
    print("session ready")

    def utcnow():
        now = datetime.datetime.utcnow()
        return now.strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        yield session.register(utcnow, u'com.myapp.date')
        print("procedure registered")
    except Exception as e:
        print("could not register procedure: {0}".format(e))


if __name__ == "__main__":
    run([component])



