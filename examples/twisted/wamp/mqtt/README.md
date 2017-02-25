# MQTT Bridge

Crossbar.io includes a MQTT bridge that not only makes it a full scale, great MQTT broker on its own, but also allows WAMP and MQTT publishers and subscribers talk to each other transparently.

This opens up whole new possibilities, eg immediately integrate MQTT client devices into a larger WAMP based application or system

## Demo

The demo make use of the MQTT bridge now included with Crossbar.io 17.2.1 and later.

You need to install `paho-mqtt` to run the MQTT client which you can
do via pip:

   pip install paho-mqtt

Then, with the Crossbar.io router running from [examples/router](https://github.com/crossbario/autobahn-python/tree/master/examples/router) dir you
can start up either the WAMP or MQTT client first (ideally in
different shells):

   python wamp-client.py
   python mqtt-client.py

They both subscribe to `mqtt.test_topic` and then publish some data to
that same topic (so try starting them in different orders etc).

## Configuration

To configure MQTT in Crossbar.io, add a MQTT transport item to a router worker like here:


```
"transports": [
    {
        "type": "mqtt",
        "endpoint": {
            "type": "tcp",
            "port": 1883
        },
        "options": {
            "realm": "crossbardemo",
            "role": "anonymous"
        }
    }
]
```

Besides the listening endpoint configuration, you can configure the mapping to a WAMP realm.
