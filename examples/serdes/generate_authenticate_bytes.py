#!/usr/bin/env python
"""
Generate serialized bytes for AUTHENTICATE message test vectors.
"""
import binascii
import txaio
txaio.use_asyncio()

from autobahn.wamp.message import Authenticate
from autobahn.wamp.serializer import create_transport_serializer

# Create a basic AUTHENTICATE message
msg = Authenticate(signature="gir1mSx+deCDUV7FgLvsQNTi6n3W/Z/WcZ/OT9RwdZY=")

print(f"Message: {msg}")
print(f"Signature: {msg.signature}")
print(f"Extra: {msg.extra}")
print()

# Serialize with each serializer
for serializer_id in ["json", "msgpack", "cbor", "ubjson"]:
    serializer = create_transport_serializer(serializer_id)
    serialized_bytes, is_binary = serializer.serialize(msg)

    print(f"{serializer_id}:")
    print(f"  bytes_hex: {binascii.hexlify(serialized_bytes).decode('ascii')}")
    if not is_binary:
        print(f"  bytes: {serialized_bytes.decode('utf-8')}")
    print()
