from os import environ

from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.wamp import ApplicationRunner
from autobahn.wamp.types import PublishOptions

from twisted.internet.defer import inlineCallbacks


class Component(ApplicationSession):
    topic = u'mqtt.test_topic'

    @inlineCallbacks
    def onJoin(self, details):
        print("session attached {}".format(details))

        yield self.subscribe(self.on_event, self.topic)
        print("Subscribed to '{}'".format(self.topic))

        # if you send args, then all args (and kwargs) in the publish
        # are encoded into a JSON body as "the" MQTT message. Here we
        # also ask WAMP to send our message back to us.
        yield self.publish(
            u"mqtt.test_topic", "some data via WAMP",
            options=PublishOptions(exclude_me=False),
        )

        # if you send *just* mqtt_qos and mqtt_message kwargs, and no
        # args then it will take mqtt_message as "the" payload
        yield self.publish(
            u"mqtt.test_topic",
            mqtt_qos=0,
            mqtt_message="hello from WAMP",
        )

    def on_event(self, *args, **kw):
        print("'{}' event: args={}, kwargs={}".format(self.topic, args, kw))


if __name__ == '__main__':
    runner = ApplicationRunner(
        environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://127.0.0.1:8080/ws"),
        u"crossbardemo",
    )
    runner.run(Component)
