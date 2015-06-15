## Unix/RawSocket example

This shows how to configure and use alternative WAMP protocols and
transports. You will need to change the configuration of your WAMP
Router to listen on the correct sockets. For crossbar.io, the
following ``transports`` snippet will do:

```javascript
{
# ...
    "workers": [
        {
            "type": "router",
# ...
            "transports": [
                {
                    "type": "websocket",
                    "endpoint": {
                        "type": "unix",
                        "path": "/tmp/cb-socket"
                    }
                },
                {
                    "type": "websocket",
                    "endpoint": {
                        "type": "tcp",
                        "version": 4,
                        "interface": "127.0.0.1",
                        "port": 4321
                    }
                },
                {
                    "type": "rawsocket",
                    "endpoint": {
                        "type": "unix",
                        "path": "/tmp/cb-raw"
                    }
                }
            ]
        }
    ]
}
```