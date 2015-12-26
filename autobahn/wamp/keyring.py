###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from __future__ import absolute_import

import os
import json
import binascii

__all__ = (
    'KeyRing',
)

try:
    import nacl  # noqa
    HAS_NACL = True
except ImportError:
    HAS_NACL = False


class EncryptedPayload(object):

    def __init__(self, algo, pkey, serializer, payload):
        self.algo = algo
        self.pkey = pkey
        self.serializer = serializer
        self.payload = payload


if HAS_NACL:
    from nacl.encoding import Base64Encoder
    from nacl.public import PrivateKey, Box
    from nacl.utils import random

    from pytrie import StringTrie

    class KeyRing(object):
        """
        In WAMP, a WAMP client connected to a router in general will
        send and receive WAMP messages containing application payload
        in the "args" and "kwargs" message fields.

        Futher, a WAMP client will send the following WAMP message types:

          * PUBLISH
          * CALL
          * YIELD
          * ERROR

        and will receive the following message types

          * EVENT
          * RESULT
          * ERROR
          * INVOCATION

        A keyring maps an URI to a pair of Ed25519 keys, one for the
        sending side, and one for the receiving side.

        A client wishing to publish to topic T1 first looks up T1 in
        a keyring. This will return the pair of keys (Sender_key, Receiver_key)
        that have been stored under an URI K1 such that K1 is a longest match of T1.

        The client generates a new random message key and encrypt the
        message. The symmetric message encrypted key is then encrypted using
        the Pub(Receiver_key) and Priv(Sender_key). This encrypted symmetric key
        is attached to the WAMP message in `option.message_key`.
        """

        def __init__(self):
            self._uri_map = StringTrie()

        def add(self, uri_prefix, key_base64=None):
            if uri_prefix not in self._uri_map:
                if key_base64:
                    key = PrivateKey(key_base64, encoder=Base64Encoder)
                    box = Box(key, key.public_key)
                else:
                    box = None
                self._uri_map[uri_prefix] = box
                print("key set for {}".format(uri_prefix))

        def check(self, uri):
            """
            Return True if sending a message to the URI should have it's
            application payload args and kwargs encrypted.
            """
            try:
                box = self._uri_map.longest_prefix_value(uri)
                return box is not None
            except KeyError:
                return False

        def encrypt(self, uri, args=None, kwargs=None):
            box = self._uri_map.longest_prefix_value(uri)
            payload = {
                u'uri': uri,
                u'args': args,
                u'kwargs': kwargs
            }
            nonce = random(Box.NONCE_SIZE)
            payload_ser = json.dumps(payload)
            payload_encr = box.encrypt(payload_ser, nonce, encoder=Base64Encoder)
            payload_bytes = payload_encr.encode().decode('ascii')
            payload_key = binascii.b2a_base64(os.urandom(32)).strip().decode('ascii')

            return EncryptedPayload(u'ed25519-sha512', payload_key, u'json', payload_bytes)

        def decrypt(self, uri, encrypted_payload):
            box = self._uri_map.longest_prefix_value(uri)
            payload_ser = box.decrypt(encrypted_payload.payload, encoder=Base64Encoder)
            payload = json.loads(payload_ser)
            return payload[u'uri'], payload[u'args'], payload[u'kwargs']

else:

    KeyRing = type(None)
