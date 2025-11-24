#!/usr/bin/env python
"""
Generate serialized bytes for INTERRUPT message test vectors.
"""

import binascii
import txaio

txaio.use_asyncio()

from autobahn.wamp.message import Interrupt
from autobahn.wamp.serializer import create_transport_serializer

# Create a basic INTERRUPT message
msg = Interrupt(request=6131533)

print(f"Message: {msg}")
print(f"Request: {msg.request}")
print(f"Mode: {msg.mode}")
print(f"Reason: {msg.reason}")
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
