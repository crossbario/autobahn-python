###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
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

import binascii
import struct
from typing import Callable, Optional, Union

import txaio

from autobahn import util
from autobahn.wamp.interfaces import ISecurityModule, ICryptosignKey, ISession
from autobahn.wamp.types import Challenge

__all__ = [
    'HAS_CRYPTOSIGN',
]

try:
    # try to import everything we need for WAMP-cryptosign
    from nacl import encoding, signing, bindings
    from nacl.signing import SignedMessage
except ImportError:
    HAS_CRYPTOSIGN = False
else:
    HAS_CRYPTOSIGN = True
    __all__.append('CryptosignKey')


def _unpack(keydata):
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


def _pack(keyparts):
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
    Parse an OpenSSH Ed25519 public key from a string into a raw public key.

    Example input:

        ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJukDU5fqXv/yVhSirsDWsUFyOodZyCSLxyitPPzWJW9 oberstet@office-corei7

    :param keydata: The OpenSSH Ed25519 public key data to parse.
    :type keydata: str

    :returns: pair of raw public key (32 bytes) and comment
    :rtype: tuple
    """
    if type(keydata) != str:
        raise Exception("invalid type {} for keydata".format(type(keydata)))

    parts = keydata.strip().split()
    if len(parts) != 3:
        raise Exception('invalid SSH Ed25519 public key')
    algo, keydata, comment = parts

    if algo != 'ssh-ed25519':
        raise Exception('not a Ed25519 SSH public key (but {})'.format(algo))

    blob = binascii.a2b_base64(keydata)

    try:
        key = _unpack(blob)[1]
    except Exception as e:
        raise Exception('could not parse key ({})'.format(e))

    if len(key) != 32:
        raise Exception('invalid length {} for embedded raw key (must be 32 bytes)'.format(len(key)))

    return key, comment


class _SSHPacketReader:
    """
    Read OpenSSH packet format which is used for key material.
    """

    def __init__(self, packet):
        self._packet = packet
        self._idx = 0
        self._len = len(packet)

    def get_remaining_payload(self):
        return self._packet[self._idx:]

    def get_bytes(self, size):
        if self._idx + size > self._len:
            raise Exception('incomplete packet')

        value = self._packet[self._idx:self._idx + size]
        self._idx += size
        return value

    def get_uint32(self):
        return struct.unpack('>I', self.get_bytes(4))[0]

    def get_string(self):
        return self.get_bytes(self.get_uint32())


def _makepad(size: int) -> bytes:
    assert 0 <= size < 255
    return b''.join(x.to_bytes(1, byteorder='big') for x in range(1, size + 1))


def _read_ssh_ed25519_privkey(keydata):
    """
    Parse an OpenSSH Ed25519 private key from a string into a raw private key.

    Example input:

        -----BEGIN OPENSSH PRIVATE KEY-----
        b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
        QyNTUxOQAAACCbpA1OX6l7/8lYUoq7A1rFBcjqHWcgki8corTz81iVvQAAAKDWjZ0Y1o2d
        GAAAAAtzc2gtZWQyNTUxOQAAACCbpA1OX6l7/8lYUoq7A1rFBcjqHWcgki8corTz81iVvQ
        AAAEArodzIMjH9MOBz0X+HDvL06rEJOMYFhzGQ5zXPM7b7fZukDU5fqXv/yVhSirsDWsUF
        yOodZyCSLxyitPPzWJW9AAAAFm9iZXJzdGV0QG9mZmljZS1jb3JlaTcBAgMEBQYH
        -----END OPENSSH PRIVATE KEY-----


    :param keydata: The OpenSSH Ed25519 private key data to parse.
    :type keydata: str

    :returns: pair of raw private key (32 bytes) and comment
    :rtype: tuple
    """

    # Some pointers:
    # https://github.com/ronf/asyncssh/blob/master/asyncssh/public_key.py
    # https://github.com/ronf/asyncssh/blob/master/asyncssh/ed25519.py
    # crypto_sign_ed25519_sk_to_seed
    # https://github.com/jedisct1/libsodium/blob/master/src/libsodium/crypto_sign/ed25519/sign_ed25519_api.c#L27
    # https://tools.ietf.org/html/draft-bjh21-ssh-ed25519-02
    # http://blog.oddbit.com/2011/05/08/converting-openssh-public-keys/

    SSH_BEGIN = '-----BEGIN OPENSSH PRIVATE KEY-----'
    SSH_END = '-----END OPENSSH PRIVATE KEY-----'
    OPENSSH_KEY_V1 = b'openssh-key-v1\0'

    if not (keydata.startswith(SSH_BEGIN) and keydata.endswith(SSH_END)):
        raise Exception('invalid OpenSSH private key (does not start/end with OPENSSH preamble)')

    ssh_end = keydata.find(SSH_END)
    keydata = keydata[len(SSH_BEGIN):ssh_end]
    keydata = ''.join(x.strip() for x in keydata.split())
    blob = binascii.a2b_base64(keydata)

    blob = blob[len(OPENSSH_KEY_V1):]
    packet = _SSHPacketReader(blob)

    cipher_name = packet.get_string()
    kdf = packet.get_string()
    packet.get_string()  # kdf_data
    nkeys = packet.get_uint32()
    packet.get_string()  # public_key
    key_data = packet.get_string()
    mac = packet.get_remaining_payload()

    block_size = 8

    if cipher_name != b'none':
        raise Exception('encrypted private keys not supported (please remove the passphrase from your private key or use SSH agent)')

    if kdf != b'none':
        raise Exception('passphrase encrypted private keys not supported')

    if nkeys != 1:
        raise Exception('multiple private keys in a key file not supported (found {} keys)'.format(nkeys))

    if mac:
        raise Exception('invalid OpenSSH private key (found remaining payload for mac)')

    packet = _SSHPacketReader(key_data)

    packet.get_uint32()  # check1
    packet.get_uint32()  # check2

    alg = packet.get_string()

    if alg != b'ssh-ed25519':
        raise Exception('invalid key type: we only support Ed25519 (found "{}")'.format(alg.decode('ascii')))

    vk = packet.get_string()
    sk = packet.get_string()

    if len(vk) != bindings.crypto_sign_PUBLICKEYBYTES:
        raise Exception('invalid public key length')

    if len(sk) != bindings.crypto_sign_SECRETKEYBYTES:
        raise Exception('invalid public key length')

    comment = packet.get_string()                             # comment
    pad = packet.get_remaining_payload()

    if len(pad) and (len(pad) >= block_size or pad != _makepad(len(pad))):
        raise Exception('invalid OpenSSH private key (padlen={}, actual_pad={}, expected_pad={})'.format(len(pad), pad, _makepad(len(pad))))

    # secret key (64 octets) = 32 octets seed || 32 octets secret key derived of seed
    seed = sk[:bindings.crypto_sign_SEEDBYTES]

    comment = comment.decode('ascii')

    return seed, comment


def _read_signify_ed25519_signature(signature_file):
    """
    Read a Ed25519 signature file created with OpenBSD signify.

    http://man.openbsd.org/OpenBSD-current/man1/signify.1
    """
    with open(signature_file) as f:
        # signature file format: 2nd line is base64 of 'Ed' || 8 random octets || 64 octets Ed25519 signature
        sig = binascii.a2b_base64(f.read().splitlines()[1])[10:]
        if len(sig) != 64:
            raise Exception('bogus Ed25519 signature: raw signature length was {}, but expected 64'.format(len(sig)))
        return sig


def _read_signify_ed25519_pubkey(pubkey_file):
    """
    Read a public key from a Ed25519 key pair created with OpenBSD signify.

    http://man.openbsd.org/OpenBSD-current/man1/signify.1
    """
    with open(pubkey_file) as f:
        # signature file format: 2nd line is base64 of 'Ed' || 8 random octets || 32 octets Ed25519 public key
        pubkey = binascii.a2b_base64(f.read().splitlines()[1])[10:]
        if len(pubkey) != 32:
            raise Exception('bogus Ed25519 public key: raw key length was {}, but expected 32'.format(len(pubkey)))
        return pubkey


def _qrcode_from_signify_ed25519_pubkey(pubkey_file, mode='text'):
    """

    Usage:

    1. Get the OpenBSD 5.7 release public key from here

        http://cvsweb.openbsd.org/cgi-bin/cvsweb/src/etc/signify/Attic/openbsd-57-base.pub?rev=1.1

    2. Generate QR Code and print to terminal

        print(cryptosign._qrcode_from_signify_ed25519_pubkey('openbsd-57-base.pub'))

    3. Compare to (scroll down) QR code here

        https://www.openbsd.org/papers/bsdcan-signify.html
    """
    assert(mode in ['text', 'svg'])

    import pyqrcode

    with open(pubkey_file) as f:
        pubkey = f.read().splitlines()[1]

        qr = pyqrcode.create(pubkey, error='L', mode='binary')

        if mode == 'text':
            return qr.terminal()

        elif mode == 'svg':
            import io
            data_buffer = io.BytesIO()

            qr.svg(data_buffer, omithw=True)

            return data_buffer.getvalue()

        else:
            raise Exception('logic error')


def _verify_signify_ed25519_signature(pubkey_file, signature_file, message):
    """
    Verify a Ed25519 signature created with OpenBSD signify.

    This will raise a `nacl.exceptions.BadSignatureError` if the signature is bad
    and return silently when the signature is good.

    Usage:

    1. Create a signature:

        signify-openbsd -S -s ~/.signify/crossbario-trustroot.sec -m .profile

    2. Verify the signature

        from autobahn.wamp import cryptosign

        with open('.profile', 'rb') as f:
            message = f.read()
            cryptosign._verify_signify_ed25519_signature('.signify/crossbario-trustroot.pub', '.profile.sig', message)

    http://man.openbsd.org/OpenBSD-current/man1/signify.1
    """
    pubkey = _read_signify_ed25519_pubkey(pubkey_file)
    verify_key = signing.VerifyKey(pubkey)
    sig = _read_signify_ed25519_signature(signature_file)
    verify_key.verify(message, sig)


# CryptosignKey from
#   - raw byte string or file with raw bytes
#   - SSH private key string or key file
#   - SSH agent proxy
#
# VerifyKey from
#   - raw byte string or file with raw bytes
#   - SSH public key string or key file

if HAS_CRYPTOSIGN:

    def format_challenge(challenge: Challenge, channel_id_raw: Optional[bytes], channel_id_type: Optional[str]) -> bytes:
        """
        Format the challenge based on provided parameters

        :param challenge: The WAMP-cryptosign challenge object for which a signature should be computed.
        :param channel_id_raw: The channel ID when channel_id_type is 'tls-unique'.
        :param channel_id_type: The type of the channel id, currently handles 'tls-unique' and
            ignores otherwise.
        """
        if not isinstance(challenge, Challenge):
            raise Exception(
                "challenge must be instance of autobahn.wamp.types.Challenge, not {}".format(type(challenge)))

        if 'challenge' not in challenge.extra:
            raise Exception("missing challenge value in challenge.extra")

        # the challenge sent by the router (a 32 bytes random value)
        challenge_hex = challenge.extra['challenge']

        if type(challenge_hex) != str:
            raise Exception("invalid type {} for challenge (expected a hex string)".format(type(challenge_hex)))

        if len(challenge_hex) != 64:
            raise Exception("unexpected challenge (hex) length: was {}, but expected 64".format(len(challenge_hex)))

        # the challenge for WAMP-cryptosign is a 32 bytes random value in Hex encoding (that is, a unicode string)
        challenge_raw = binascii.a2b_hex(challenge_hex)

        if channel_id_type == 'tls-unique':
            assert len(
                channel_id_raw) == 32, 'unexpected TLS transport channel ID length (was {}, but expected 32)'.format(
                len(channel_id_raw))

            # with TLS channel binding of type "tls-unique", the message to be signed by the client actually
            # is the XOR of the challenge and the TLS channel ID
            data = util.xor(challenge_raw, channel_id_raw)
        elif channel_id_type is None:
            # when no channel binding was requested, the message to be signed by the client is the challenge only
            data = challenge_raw
        else:
            assert False, 'invalid channel_id_type "{}"'.format(channel_id_type)

        return data

    def sign_challenge(data: bytes, signer_func: Callable) -> bytes:
        """
        Sign the provided data using the provided signer.

        :param data: challenge to sign
        :param signer_func: The callable function to use for signing
        :returns: A Deferred/Future that resolves to the computed signature.
        :rtype: str
        """
        # a raw byte string is signed, and the signature is also a raw byte string
        d1 = signer_func(data)

        # asyncio lacks callback chaining (and we cannot use co-routines, since we want
        # to support older Pythons), hence we need d2
        d2 = txaio.create_future()

        def process(signature_raw):
            # convert the raw signature into a hex encode value (unicode string)
            signature_hex = binascii.b2a_hex(signature_raw).decode('ascii')

            # we return the concatenation of the signature and the message signed (96 bytes)
            data_hex = binascii.b2a_hex(data).decode('ascii')

            sig = signature_hex + data_hex
            txaio.resolve(d2, sig)

        txaio.add_callbacks(d1, process, None)

        return d2

    @util.public
    class CryptosignKey(object):
        """
        A cryptosign private key for signing, and hence usable for authentication or a
        public key usable for verification (but can't be used for signing).
        """

        def __init__(self, key, can_sign: bool, security_module: Optional[ISecurityModule] = None,
                     key_no: Optional[int] = None, comment: Optional[str] = None) -> None:
            if not (isinstance(key, signing.VerifyKey) or isinstance(key, signing.SigningKey)):
                raise Exception("invalid type {} for key".format(type(key)))

            assert (can_sign and isinstance(key, signing.SigningKey)) or (not can_sign and isinstance(key, signing.VerifyKey))
            self._key = key
            self._can_sign = can_sign
            self._security_module = security_module
            self._key_no = key_no
            self._comment = comment

        @property
        def security_module(self) -> Optional['ISecurityModule']:
            """
            Implements :meth:`autobahn.wamp.interfaces.IKey.security_module`.
            """
            return self._security_module

        @property
        def key_no(self) -> Optional[int]:
            """
            Implements :meth:`autobahn.wamp.interfaces.IKey.key_no`.
            """
            return self._key_no

        @property
        def comment(self) -> Optional[str]:
            """
            Implements :meth:`autobahn.wamp.interfaces.IKey.comment`.
            """
            return self._comment

        @property
        def key_type(self) -> str:
            """
            Implements :meth:`autobahn.wamp.interfaces.IKey.key_type`.
            """
            return 'cryptosign'

        @property
        def can_sign(self) -> bool:
            """
            Implements :meth:`autobahn.wamp.interfaces.IKey.can_sign`.
            """
            return self._can_sign

        @util.public
        def sign(self, data: bytes) -> bytes:
            """
            Implements :meth:`autobahn.wamp.interfaces.IKey.sign`.
            """
            if not self._can_sign:
                raise Exception("a signing key required to sign")

            if type(data) != bytes:
                raise Exception("data to be signed must be binary")

            sig: SignedMessage = self._key.sign(data)

            # we only return the actual signature! if we return "sig",
            # it gets coerced into the concatenation of message + signature
            # not sure which order, but we don't want that. we only want
            # the signature
            return txaio.create_future_success(sig.signature)

        @util.public
        def sign_challenge(self, session: ISession, challenge: Challenge,
                           channel_id_type: Optional[str] = None) -> bytes:
            """
            Implements :meth:`autobahn.wamp.interfaces.ICryptosignKey.sign_challenge`.
            """
            # get the TLS channel ID of the underlying TLS connection
            if channel_id_type in session._transport.transport_details.channel_id:
                channel_id = session._transport.transport_details.channel_id.get(channel_id_type, None)
            else:
                channel_id_type = None
                channel_id = None

            data = format_challenge(challenge, channel_id, channel_id_type)

            return sign_challenge(data, self.sign)

        @util.public
        def public_key(self, binary: bool = False) -> Union[str, bytes]:
            """
            Returns the public key part of a signing key or the (public) verification key.

            :returns: The public key in Hex encoding.
            :rtype: str or None
            """
            if isinstance(self._key, signing.SigningKey):
                key = self._key.verify_key
            else:
                key = self._key

            if binary:
                return key.encode()
            else:
                return key.encode(encoder=encoding.HexEncoder).decode('ascii')

        @util.public
        @classmethod
        def from_bytes(cls, key_data: bytes, comment: Optional[str] = None) -> 'CryptosignKey':
            if not (comment is None or type(comment) == str):
                raise ValueError("invalid type {} for comment".format(type(comment)))

            if type(key_data) != bytes:
                raise ValueError("invalid key type {} (expected binary)".format(type(key_data)))

            if len(key_data) != 32:
                raise ValueError("invalid key length {} (expected 32)".format(len(key_data)))

            key = signing.SigningKey(key_data)
            return cls(key=key, can_sign=True, comment=comment)

        @util.public
        @classmethod
        def from_file(cls, filename: str, comment: Optional[str] = None) -> 'CryptosignKey':
            """
            Load an Ed25519 (private) signing key (actually, the seed for the key) from a raw file of 32 bytes length.
            This can be any random byte sequence, such as generated from Python code like

                os.urandom(32)

            or from the shell

                dd if=/dev/urandom of=client02.key bs=1 count=32

            :param filename: Filename of the key.
            :param comment: Comment for key (optional).
           """
            if not (comment is None or type(comment) == str):
                raise Exception("invalid type {} for comment".format(type(comment)))

            if type(filename) != str:
                raise Exception("invalid type {} for filename".format(filename))

            with open(filename, 'rb') as f:
                key_data = f.read()

            return cls.from_bytes(key_data, comment=comment)

        @util.public
        @classmethod
        def from_ssh_file(cls, filename: str) -> 'CryptosignKey':
            """
            Load an Ed25519 key from a SSH key file. The key file can be a (private) signing
            key (from a SSH private key file) or a (public) verification key (from a SSH
            public key file). A private key file must be passphrase-less.
            """

            with open(filename, 'rb') as f:
                key_data = f.read().decode('utf-8').strip()
            return cls.from_ssh_bytes(key_data)

        @util.public
        @classmethod
        def from_ssh_bytes(cls, key_data: str) -> 'CryptosignKey':
            """
            Load an Ed25519 key from SSH key file. The key file can be a (private) signing
            key (from a SSH private key file) or a (public) verification key (from a SSH
            public key file). A private key file must be passphrase-less.
            """
            SSH_BEGIN = '-----BEGIN OPENSSH PRIVATE KEY-----'
            if key_data.startswith(SSH_BEGIN):
                # OpenSSH private key
                key_data, comment = _read_ssh_ed25519_privkey(key_data)
                key = signing.SigningKey(key_data, encoder=encoding.RawEncoder)
                can_sign = True
            else:
                # OpenSSH public key
                key_data, comment = _read_ssh_ed25519_pubkey(key_data)
                key = signing.VerifyKey(key_data)
                can_sign = False

            return cls(key=key, can_sign=can_sign, comment=comment)

        @classmethod
        def from_seedphrase(cls, seedphrase: str, index: int = 0) -> 'CryptosignKey':
            """
            Create a private key from the given BIP-39 mnemonic seed phrase and index,
            which can be used to sign and create signatures.

            :param seedphrase: The BIP-39 seedphrase ("Mnemonic") from which to derive the account.
            :param index: The account index in account hierarchy defined by the seedphrase.
            :return: New instance of :class:`EthereumKey`
            """
            try:
                from autobahn.xbr._mnemonic import mnemonic_to_private_key
            except ImportError as e:
                raise RuntimeError('package autobahn[xbr] not installed ("{}")'.format(e))

            # BIP44 path for WAMP
            # https://github.com/wamp-proto/wamp-proto/issues/401
            # https://github.com/satoshilabs/slips/pull/1322
            derivation_path = "m/44'/655'/0'/0/{}".format(index)

            key_raw = mnemonic_to_private_key(seedphrase, derivation_path)
            assert type(key_raw) == bytes
            assert len(key_raw) == 32

            # create WAMP-Cryptosign key object from raw bytes
            key = cls.from_bytes(key_raw)

            return key

    ICryptosignKey.register(CryptosignKey)

    __all__.extend(['CryptosignKey', 'format_challenge', 'sign_challenge'])
