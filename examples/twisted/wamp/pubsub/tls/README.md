# TLS

This demonstrates how to use a custom `sslContextFactory` for
SSL4ClientEndpoints to control how TLS verification is
done. Specifically, we connect via wss:// to a TLS-enabled backend
with a self-signed certificate.

Use the script "create-self-signed-cert.sh" to create a new
certificate in `server.crt` (with corresponding private key
`server.key`). You can teach crossbar about your certificate by adding
a "transport" configuration like the following (this can be dropped
straight into examples/router/.crossbar/config.json)::

    {
        "type": "websocket",
        "id": "tls_test0",
        "endpoint": {
            "type": "tcp",
            "port": 8083,
            "tls": {
                "key": "../../twisted/wamp/pubsub/tls/server.key",
                "certificate": "../../twisted/wamp/pubsub/tls/server.crt"
            }
        }
    }

`backend_selfsigned.py` is designed to connect to a transport
configured as above, and also needs access to the `server.crt`
file. So you can simply run `create-self-signed-cert.sh` here and the
above should read the same files directly.
