#!/usr/bin/env python
"""
Generate serialized bytes for WELCOME message test vectors.
"""

import binascii
import txaio

txaio.use_asyncio()

from autobahn.wamp.message import Welcome
from autobahn.wamp.serializer import create_transport_serializer
from autobahn.wamp.role import RoleBrokerFeatures, RoleDealerFeatures

# Create a basic WELCOME message
msg = Welcome(
    session=9129137332,
    roles={"broker": RoleBrokerFeatures(), "dealer": RoleDealerFeatures()},
)

print(f"Message: {msg}")
print(f"Session: {msg.session}")
print(f"Roles: {msg.roles}")
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
