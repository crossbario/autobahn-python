
import os
import sys
import json
import hmac
import hashlib
import base64
import binascii
from pprint import pprint


if len(sys.argv) != 2:
    print("usage: {} password".format(sys.argv[0]))
    sys.exit(2)

password = sys.argv[1].encode('ascii')

from argon2.low_level import hash_secret
from argon2.low_level import Type

secret = sys.argv[1].encode('ascii')
salt = os.urandom(16)

print("{} {}".format(secret, type(secret)))
print("{} {}".format(salt, type(salt)))

hash_data = hash_secret(
    secret=secret,
    salt=salt,
    time_cost=4096,  # the library recommends 2 for "server logins" (because < 0.5ms?)
    memory_cost=512,
    parallelism=2,
    hash_len=16,
    type=Type.ID,
    version=19,
)

_, tag, v, params, othersalt, h = hash_data.decode('ascii').split('$')
assert tag == 'argon2id'
assert v == 'v=19'
params = {
    k: v
    for k, v in
    [x.split('=') for x in params.split(',')]
}

#    "hash": h,

def Normalize(x):
    return x



def HMAC(key, msg):
    hm = hmac.new(key, msg)
    return hm.digest()


def SHA256(msg):
    s = hashlib.new('sha256')
    s.update(msg)
    return s.digest()

#SaltedPassword  = KDF(Normalize(password), salt, int(params['t']), int(params['m']), int(params['p']))
SaltedPassword = h.encode('ascii')
ClientKey       = HMAC(SaltedPassword, b"Client Key")
StoredKey       = SHA256(ClientKey)
ServerKey       = HMAC(SaltedPassword, b"Server Key")

key = {
    "memory": int(params['m']),
    "cost": int(params['t']),
    "parallel": int(params['p']),
#    "salt": base64.b64encode(salt).decode('ascii'),
#    "stored-key": base64.b64encode(StoredKey).decode('ascii'),
#    "server-key": base64.b64encode(ServerKey).decode('ascii'),
    "salt": binascii.b2a_hex(salt).decode('ascii'),
    "stored-key": binascii.b2a_hex(StoredKey).decode('ascii'),
    "server-key": binascii.b2a_hex(ServerKey).decode('ascii'),
}
print(json.dumps(key, indent=4))
