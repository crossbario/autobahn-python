import paho.mqtt.client as paho

# note that unlike Autobahn and Crossbar, this MQTT client is threaded
# / synchronous

client = paho.Client()
client.connect('localhost', port=1883)


def on_connect(client, userdata, flags, rc):
    print("on_connect({}, {}, {}, {})".format(client, userdata, flags, rc))
    client.subscribe("mqtt.test_topic", qos=0)
    client.publish(
        "mqtt.test_topic",
        "some data via MQTT",
    )


def on_message(client, userdata, msg):
    print("{}: {}".format(msg.topic, msg.payload))


client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
