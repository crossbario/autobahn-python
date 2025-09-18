import base64
import binascii
import hashlib
import hmac
import json
import os
import sys

from argon2.low_level import Type, hash_secret
from passlib.utils import saslprep

if len(sys.argv) not in (2, 3):
    print("usage: {} password".format(sys.argv[0]))
    sys.exit(2)

password = sys.argv[1].encode("ascii")
if len(sys.argv) == 3:
    m = hashlib.sha256()
    m.update(sys.argv[2].encode("utf8"))
    salt = m.digest()[:16]
    # salt = binascii.a2b_hex(sys.argv[2].encode('ascii'))
    assert len(salt) == 16
else:
    salt = os.urandom(16)

hash_data = hash_secret(
    secret=password,
    salt=salt,
    time_cost=4096,
    memory_cost=512,
    parallelism=1,
    hash_len=32,
    type=Type.ID,
    version=19,
)

_, tag, v, params, othersalt, salted_password = hash_data.decode("ascii").split("$")
assert tag == "argon2id"
assert v == "v=19"  # argon's version 1.3 is represented as 0x13, which is 19 decimal...
params = {k: v for k, v in [x.split("=") for x in params.split(",")]}

salted_password = salted_password.encode("ascii")
client_key = hmac.new(salted_password, b"Client Key", hashlib.sha256).digest()
stored_key = hashlib.new("sha256", client_key).digest()
server_key = hmac.new(salted_password, b"Server Key", hashlib.sha256).digest()

# this can be copy-pasted into the config.json for a Crossbar.io
# static-configured scram principal; see the example router config
key = {
    "kdf": "argon2id-13",
    "memory": int(params["m"]),
    "iterations": int(params["t"]),
    "salt": binascii.b2a_hex(salt).decode("ascii"),
    "stored-key": binascii.b2a_hex(stored_key).decode("ascii"),
    "server-key": binascii.b2a_hex(server_key).decode("ascii"),
}
print(json.dumps(key, indent=4))
