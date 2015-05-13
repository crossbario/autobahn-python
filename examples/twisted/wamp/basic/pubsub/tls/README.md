# TLS

This demonstrates how to use a custom `sslContextFactory` for
SSL4ClientEndpoints to control how TLS verification is
done. Specifically, we connect via wss:// to a TLS-enabled backend
with a self-signed certificate.

Use the script "create-self-signed-cert.sh" to create a new
certificate in `server.crt` (with corresponding private key
`server.key`). You can teach crossbar about your certificate by adding
a "transport" configuration like the following::

    {
        "type": "websocket",
        "id": "tls_test0",
        "endpoint": {
            "type": "tcp",
            "port": 6464,
            "tls": {
                "key": "./server.key",
                "certificate": "./server.crt"
            }
        }
    }

`backend_selfsigned.py` is designed to connect to a transport
configured as above, and also needs access to the `server.crt` file.
