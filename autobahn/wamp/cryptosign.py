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

import binascii
import struct

import six

from nacl import public, encoding, signing


def unpack(keydata):
    parts = []
    while keydata:
        # read the length of the data
        dlen = struct.unpack('>I', keydata[:4])[0]

        # read in <length> bytes
        data, keydata = keydata[4:dlen + 4], keydata[4 + dlen:]
        parts.append(data)
    return parts


class Key(object):

    def __init__(self, key, comment, is_private):
        self._key = key
        self._comment = comment
        self._is_private = is_private

    def sign(self, data):
        if not self._is_private:
            raise Exception("private key required to sign")
        if type(data) != six.binary_type:
            raise Exception("data to be signed must be binary")
        return self._key.sign(data)

    def sign_challenge(self, challenge):
        data = challenge.extra['challenge']
        signature = self.sign(binascii.a2b_hex(data))
        return binascii.b2a_hex(signature).decode('ascii')

    def public_key(self):
        """
        Returns the public key.
        """
        if isinstance(self._key, signing.SigningKey):
            key = self._key.verify_key.encode(encoder=encoding.HexEncoder)
        elif isinstance(self._key, public.PrivateKey):
            key = self._key.public_key.encode(encoder=encoding.HexEncoder)
        else:
            key = self._key.encode(encoder=encoding.HexEncoder)
        return key.decode('ascii')

    def __str__(self):
        return u'Key(comment="{}", is_private={}, public_key={})'.format(self._comment, self._is_private, self.public_key())

    @classmethod
    def from_raw(cls, filename, comment=None):
        """
        Load a Ed25519 private key (actually, the seed for the key) from a raw file of 32 bytes length.
        This can be any random byte sequence, such as generated from Python code like

            os.urandom(32)

        or from the shell

            dd if=/dev/urandom of=client02.key bs=1 count=32
        """
        with open(filename, 'rb') as f:
            keydata = f.read()
        # key = public.PrivateKey(keydata)
        key = signing.SigningKey(keydata)
        return cls(key, comment, True)

    @classmethod
    def from_ssh_agent(cls, comment=None):
        """
        Create a proxy for a key held in SSH agent.

        * run an SSH key agent under a dedicated auth agent account
        * add private keys for WAMP client running on this host under the agent
        * have the SSH agent Unix domain socket only accesible for the WAMP client (or WAMP router)
        * nobody but the dedicated auth agent account has access to private keys
        * access to the auth agent and it's signing service is restricted
        """
        raise Exception("not yet implemented")

    @classmethod
    def from_ssh(cls, filename):
        """
        Load a Ed25519 public key from a SSH public key file.
        """
        # https://tools.ietf.org/html/draft-bjh21-ssh-ed25519-02
        # http://blog.oddbit.com/2011/05/08/converting-openssh-public-keys/

        SSH_BEGIN = u'-----BEGIN OPENSSH PRIVATE KEY-----'
        SSH_END = u'-----END OPENSSH PRIVATE KEY-----'
        with open(filename, 'r') as f:
            keydata = f.read().strip()

        if keydata.startswith(SSH_BEGIN):
            # private key
            ssh_end = keydata.find(SSH_END)
            keydata = keydata[len(SSH_BEGIN):ssh_end]
            keydata = u''.join([x.strip() for x in keydata.split()])
            blob = binascii.a2b_base64(keydata)
            print(blob)
            prefix = 'openssh-key-v1\x00'
            data = unpack(blob[len(prefix):])
            print(data)
            raise Exception("loading private keys not implemented")
        else:
            # public key
            try:
                algo, keydata, comment = keydata.split()
                blob = binascii.a2b_base64(keydata)
                keydata = unpack(blob)[1]
            except Exception as e:
                raise Exception("could not parse key ({})".format(e))

            if algo != u'ssh-ed25519':
                raise Exception("loading keys of type {} not implemented".format(algo))

            if len(keydata) != 32:
                raise Exception("invalid length {} for embedded raw key (must be 32 bytes)".format(len(keydata)))

            key = public.PublicKey(keydata)

            return cls(key, comment, False)


if __name__ == '__main__':
    import sys

    # key = Key.from_raw(sys.argv[1], u'client02@example.com')
    key = Key.from_ssh(sys.argv[1])
    print(key)
