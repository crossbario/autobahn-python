
import os
import sys
import json
import hmac
import hashlib
import base64
import binascii
from passlib.utils import saslprep
from pprint import pprint
from argon2.low_level import hash_secret
from argon2.low_level import Type

if len(sys.argv) != 2:
    print("usage: {} password".format(sys.argv[0]))
    sys.exit(2)

password = sys.argv[1].encode('ascii')
salt = os.urandom(16)

hash_data = hash_secret(
    secret=password,
    salt=salt,
    time_cost=4096,
    memory_cost=512,
    parallelism=2,
    hash_len=16,
    type=Type.ID,
    version=19,
)

_, tag, v, params, othersalt, salted_password = hash_data.decode('ascii').split('$')
assert tag == 'argon2id'
assert v == 'v=19'
params = {
    k: v
    for k, v in
    [x.split('=') for x in params.split(',')]
}

salted_password = salted_password.encode('ascii')
client_key = hmac.new(salted_password, b"Client Key", hashlib.sha256).digest()
stored_key = hashlib.new('sha256', client_key).digest()
server_key = hmac.new(salted_password, b"Server Key", hashlib.sha256).digest()

# this can be copy-pasted into the config.json for a Crossbar.io
# static-configured scram principal; see the example router config
key = {
    "memory": int(params['m']),
    "cost": int(params['t']),
    "parallel": int(params['p']),
    "salt": binascii.b2a_hex(salt).decode('ascii'),
    "stored-key": binascii.b2a_hex(stored_key).decode('ascii'),
    "server-key": binascii.b2a_hex(server_key).decode('ascii'),
}
print(json.dumps(key, indent=4))
