from __future__ import print_function
import os
import txaio

from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import SSL4ClientEndpoint
from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.internet.ssl import optionsForClientTLS, trustRootFromCertificates, Certificate, CertificateOptions
from twisted.internet import reactor

from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import Session
from autobahn.wamp.types import PublishOptions, SubscribeOptions
from autobahn.wamp.types import RegisterOptions, CallOptions


component = Component(
    transports=u'ws://localhost:8080/ws',
    realm=u'crossbardemo',
)

# @component.subscribe(
#     u"com.example.",
#     options=SubscribeOptions(match=u"prefix"),
# )
# def catch_all(*args, **kw):
#     print("catch_all({}, {})".format(args, kw))

@component.subscribe(
    u"com.example.",
    options=SubscribeOptions(match=u"prefix", details_arg='details'),
)
def an_event(details=None):
    print("topic '{}'".format(details.topic))


@component.register(
    u"com.example.progressive",
    options=RegisterOptions(details_arg='details'),
)
@inlineCallbacks
def progressive_callee(details=None):
    print("progressive", details)
    if details.progress is None:
        raise RuntimeError(
            "You can only call be with an on_progress handler"
        )
    for x in ['here are', 'some progressive', 'results']:
        details.progress(x)
        yield sleep(.5)
    return None


@component.on_join
def join(session, details):
    print("Session {} joined: {}".format(details.session, details))

    def pub(topic):
        print("publishing '{}'".format(topic))
        return session.publish(
            topic,
            options=PublishOptions(exclude_me=False),
        )

    def call_progress(topic):
        print("calling '{}' progressively".format(topic))
        def on_progress(some_data):
            print("received: '{}'".format(some_data))
        return session.call(
            topic,
            options=CallOptions(on_progress=on_progress)
        )

    reactor.callLater(1, pub, u'com.example.foo')
    reactor.callLater(2, pub, u'com.non_matching')
    reactor.callLater(3, pub, u'com.example.some.other.uri')
    reactor.callLater(4, call_progress, u'com.example.progressive')
    reactor.callLater(7, session.leave)

@component.on_leave
def leave(session, details):
    print("Session leaving: {}: {}".format(details.reason, details.message))


if __name__ == '__main__':
    run(component)
