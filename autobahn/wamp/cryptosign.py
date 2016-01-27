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
import binascii
import struct

import six
from nacl import public, encoding, signing

from txaio import create_future_success

from autobahn import util
from autobahn.wamp.types import Challenge

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import UNIXClientEndpoint

try:
    from twisted.conch.ssh.agent import SSHAgentClient
except ImportError:
    # twisted.conch is not yet fully ported to Python 3
    _HAS_SSH_AGENT_SUPPORT = False
else:
    _HAS_SSH_AGENT_SUPPORT = True


def unpack(keydata):
    """
    Unpack a SSH agent key blob into parts.

    See: http://blog.oddbit.com/2011/05/08/converting-openssh-public-keys/
    """
    parts = []
    while keydata:
        # read the length of the data
        dlen = struct.unpack('>I', keydata[:4])[0]

        # read in <length> bytes
        data, keydata = keydata[4:dlen + 4], keydata[4 + dlen:]
        parts.append(data)
    return parts


def pack(keyparts):
    """
    Pack parts into a SSH key blob.
    """
    parts = []
    for part in keyparts:
        parts.append(struct.pack('>I', len(part)))
        parts.append(part)
    return b''.join(parts)


def _read_ssh_ed25519_pubkey(keydata):
    """
    Parse a Ed25519 SSH public key from a string into a raw public key.

    :param keydata: The public Ed25519 SSH key to parse.
    :type keydata: unicode

    :returns: The raw public keys (32 bytes).
    :rtype: binary
    """
    if type(keydata) != six.text_type:
        raise Exception("invalid type {} for keydata".format(type(keydata)))

    parts = keydata.strip().split()
    if len(parts) != 3:
        raise Exception('invalid SSH Ed25519 public key')
    algo, keydata, comment = parts

    if algo != u'ssh-ed25519':
        raise Exception('not a Ed25519 SSH public key (but {})'.format(algo))

    blob = binascii.a2b_base64(keydata)

    try:
        key = unpack(blob)[1]
    except Exception as e:
        raise Exception('could not parse key ({})'.format(e))

    if len(key) != 32:
        raise Exception('invalid length {} for embedded raw key (must be 32 bytes)'.format(len(key)))

    return key


# SigningKey from
#   - raw byte string or file with raw bytes
#   - SSH private key string or key file
#   - SSH agent proxy
#
# VerifyKey from
#   - raw byte string or file with raw bytes
#   - SSH public key string or key file


class SigningKey(object):
    """
    A cryptosign private key for signing, and hence usable for authentication or a
    public key usable for verification (but can't be used for signing).
    """

    def __init__(self, key, comment=None):
        """

        :param key: A Ed25519 private signing key or a Ed25519 public verification key.
        :type key: instance of nacl.public.VerifyKey or instance of nacl.public.SigningKey
        """
        if not (isinstance(key, signing.VerifyKey) or isinstance(key, signing.SigningKey)):
            raise Exception("invalid type {} for key".format(type(key)))

        if not (comment is None or type(comment) == six.text_type):
            raise Exception("invalid type {} for comment".format(type(comment)))

        self._key = key
        self._comment = comment
        self._can_sign = isinstance(key, SigningKey)

    def __str__(self):
        return u'Key(can_sign={}, comment="{}", public_key={})'.format(self.can_sign(), self.comment(), self.public_key())

    def can_sign(self):
        """
        Check if the key can be used to sign.

        :returns: `True`, iff the key can sign.
        :rtype: bool
        """
        return self._can_sign

    def comment(self):
        """
        Get the key comment (if any).

        :returns: The comment (if any) from the key.
        :rtype: unicode or None
        """
        return self._comment

    def public_key(self, binary=False):
        """
        Returns the public key part of a signing key or the (public) verification key.

        :returns: The public key in Hex encoding.
        :rtype: unicode or None
        """
        if isinstance(self._key, signing.SigningKey):
            key = self._key.verify_key
        else:
            key = self._key

        if binary:
            return key.encode()
        else:
            return key.encode(encoder=encoding.HexEncoder).decode('ascii')

    def sign(self, data):
        """
        Sign some data.

        :param data: The data to be signed.
        :type data: bytes

        :returns: The signature.
        :rtype: bytes
        """
        if not self._is_private:
            raise Exception("private key required to sign")

        if type(data) != six.binary_type:
            raise Exception("data to be signed must be binary")

        return create_future_success(self._key.sign(data))

    @inlineCallbacks
    def sign_challenge(self, session, challenge):
        """
        Sign WAMP-cryptosign challenge.

        :param challenge: The WAMP-cryptosign challenge object for which a signature should be computed.
        :type challenge: instance of autobahn.wamp.types.Challenge

        :returns: A Deferred/Future that resolves to the computed signature.
        :rtype: unicode
        """
        if not isinstance(challenge, Challenge):
            raise Exception("challenge must be instance of autobahn.wamp.types.Challenge, not {}".format(type(challenge)))

        if u'challenge' not in challenge.extra:
            raise Exception("missing challenge value in challenge.extra")

        # the challenge sent by the router (a 32 bytes random value)
        challenge_hex = challenge.extra[u'challenge']

        # the challenge for WAMP-cryptosign is a 32 bytes random value in Hex encoding (that is, a unicode string)
        challenge_raw = binascii.a2b_hex(challenge_hex)

        # if the transport has a channel ID, the message to be signed by the client actually
        # is the XOR of the challenge and the channel ID
        channel_id_raw = session._transport.get_channel_id()
        if channel_id_raw:
            data = util.xor(challenge_raw, channel_id_raw)
        else:
            data = challenge_raw

        # a raw byte string is signed, and the signature is also a raw byte string
        signature_raw = yield self.sign(data)

        # convert the raw signature into a hex encode value (unicode string)
        signature_hex = binascii.b2a_hex(signature_raw).decode('ascii')

        # we return the concatenation of the signature and the message signed (96 bytes)
        data_hex = binascii.b2a_hex(data).decode('ascii')

        # we always return a future/deferred, so handling is uniform
        returnValue(signature_hex + data_hex)

    @classmethod
    def from_raw_key(cls, filename, comment=None):
        """
        Load an Ed25519 (private) signing key (actually, the seed for the key) from a raw file of 32 bytes length.
        This can be any random byte sequence, such as generated from Python code like

            os.urandom(32)

        or from the shell

            dd if=/dev/urandom of=client02.key bs=1 count=32

        :param filename: Filename of the key.
        :type filename: unicode
        :param comment: Comment for key (optional).
        :type comment: unicode or None
        """
        if not (comment is None or type(comment) == six.text_type):
            raise Exception("invalid type {} for comment".format(type(comment)))

        if type(filename) != six.text_type:
            raise Exception("invalid type {} for filename".format(filename))

        with open(filename, 'rb') as f:
            keydata = f.read()

        if len(keydata) != 32:
            raise Exception("invalid key length {}".format(len(keydata)))

        key = signing.SigningKey(keydata)
        return cls(key, comment)

    @classmethod
    def from_ssh_key(cls, filename):
        """
        Load an Ed25519 key from a SSH key file. The key file can be a (private) signing
        key (from a SSH private key file) or a (public) verification key (from a SSH
        public key file). A private key file must be passphrase-less.
        """
        # https://tools.ietf.org/html/draft-bjh21-ssh-ed25519-02
        # http://blog.oddbit.com/2011/05/08/converting-openssh-public-keys/

        SSH_BEGIN = u'-----BEGIN OPENSSH PRIVATE KEY-----'
        SSH_END = u'-----END OPENSSH PRIVATE KEY-----'

        with open(filename, 'r') as f:
            keydata = f.read().strip()

        if keydata.startswith(SSH_BEGIN) and keydata.endswith(SSH_END):
            # SSH private key
            # ssh_end = keydata.find(SSH_END)
            # keydata = keydata[len(SSH_BEGIN):ssh_end]
            # keydata = u''.join([x.strip() for x in keydata.split()])
            # blob = binascii.a2b_base64(keydata)
            # prefix = 'openssh-key-v1\x00'
            # data = unpack(blob[len(prefix):])
            raise Exception("loading private keys not implemented")
        else:
            # SSH public key
            keydata = _read_ssh_ed25519_pubkey(filename)
            key = public.PublicKey(keydata)
            return cls(key)


class SSHAgentSigningKey(SigningKey):
    """
    A WAMP-cryptosign signing key that is a proxy to a private Ed25510 key
    actually held in SSH agent.

    An instance of this class must be create via the class method new().
    The instance only holds the public key part, whereas the private key
    counterpart is held in SSH agent.
    """

    def __init__(self, key, comment=None, reactor=None):
        SigningKey.__init__(self, key, comment)
        if not reactor:
            from twisted.internet import reactor
        self._reactor = reactor

    @classmethod
    def new(cls, pubkey=None, reactor=None):
        """
        Create a proxy for a key held in SSH agent.

        :param pubkey: A string with a public Ed25519 key in SSH format.
        :type pubkey: unicode
        """
        if not _HAS_SSH_AGENT_SUPPORT:
            raise Exception("SSH agent integration is not supported on this platform")

        pubkey = _read_ssh_ed25519_pubkey(pubkey)

        if not reactor:
            from twisted.internet import reactor

        if "SSH_AUTH_SOCK" not in os.environ:
            raise Exception("no ssh-agent is running!")

        factory = Factory()
        factory.noisy = False
        factory.protocol = SSHAgentClient
        endpoint = UNIXClientEndpoint(reactor, os.environ["SSH_AUTH_SOCK"])
        d = endpoint.connect(factory)

        @inlineCallbacks
        def on_connect(agent):
            keys = yield agent.requestIdentities()

            # if the key is found in ssh-agent, the raw public key (32 bytes), and the
            # key comment as returned from ssh-agent
            key_data = None
            key_comment = None

            for blob, comment in keys:
                raw = unpack(blob)
                algo = raw[0]
                if algo == u'ssh-ed25519':
                    algo, _pubkey = raw
                    if _pubkey == pubkey:
                        key_data = _pubkey
                        key_comment = comment.decode('utf8')
                        break

            agent.transport.loseConnection()

            if key_data:
                key = signing.VerifyKey(key_data)
                returnValue(cls(key, key_comment, reactor))
            else:
                raise Exception("Ed25519 key not held in ssh-agent")

        return d.addCallback(on_connect)

    def sign(self, challenge):
        if "SSH_AUTH_SOCK" not in os.environ:
            raise Exception("no ssh-agent is running!")

        factory = Factory()
        factory.noisy = False
        factory.protocol = SSHAgentClient
        endpoint = UNIXClientEndpoint(self._reactor, os.environ["SSH_AUTH_SOCK"])
        d = endpoint.connect(factory)

        @inlineCallbacks
        def on_connect(agent):
            # we are now connected to the locally running ssh-agent
            # that agent might be the openssh-agent, or eg on Ubuntu 14.04 by
            # default the gnome-keyring / ssh-askpass-gnome application
            blob = pack(['ssh-ed25519', self.public_key(binary=True)])

            # now ask the agent
            signature_blob = yield agent.signData(blob, challenge)
            algo, signature = unpack(signature_blob)

            agent.transport.loseConnection()

            returnValue(signature)

        return d.addCallback(on_connect)
