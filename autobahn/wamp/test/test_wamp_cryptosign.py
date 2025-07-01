###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
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
import hashlib
import os
import unittest
from unittest.mock import Mock

import txaio

if os.environ.get("USE_TWISTED", None):
    txaio.use_twisted()
elif os.environ.get("USE_ASYNCIO", None):
    txaio.use_asyncio()
else:
    raise RuntimeError("need either USE_TWISTED=1 or USE_ASYNCIO=1")

from autobahn.wamp import types
from autobahn.wamp.auth import create_authenticator
from autobahn.wamp.cryptosign import HAS_CRYPTOSIGN, CryptosignAuthextra, _makepad

if HAS_CRYPTOSIGN:
    from nacl.encoding import HexEncoder

    from autobahn.wamp.cryptosign import CryptosignKey


import tempfile

keybody = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAa38i/4dNWFuZN/72QAJbyOwZvkUyML/u2b2B1uW4RbQAAAJj4FLyB+BS8
gQAAAAtzc2gtZWQyNTUxOQAAACAa38i/4dNWFuZN/72QAJbyOwZvkUyML/u2b2B1uW4RbQ
AAAEBNV9l6aPVVaWYgpthJwM5YJWhRjXKet1PcfHMt4oBFEBrfyL/h01YW5k3/vZAAlvI7
Bm+RTIwv+7ZvYHW5bhFtAAAAFXNvbWV1c2VyQGZ1bmt0aGF0LmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""

pubkey = """ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVp3hjHwIQyEladzd8mFcf0YSXcmyKS3qMLB7VqTQKm someuser@example.com
"""

# valid test vectors for WAMP-cryptosign signature testing
test_vectors_1 = [
    # _WITHOUT_ channel_id
    {
        "channel_id": None,
        "private_key": "4d57d97a68f555696620a6d849c0ce582568518d729eb753dc7c732de2804510",
        "challenge": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        "signature": "b32675b221f08593213737bef8240e7c15228b07028e19595294678c90d11c0cae80a357331bfc5cc9fb71081464e6e75013517c2cf067ad566a6b7b728e5d03ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
    },
    {
        "channel_id": None,
        "private_key": "d511fe78e23934b3dadb52fcd022974b80bd92bccc7c5cf404e46cc0a8a2f5cd",
        "challenge": "b26c1f87c13fc1da14997f1b5a71995dff8fbe0a62fae8473c7bdbd05bfb607d",
        "signature": "d4209ad10d5aff6bfbc009d7e924795de138a63515efc7afc6b01b7fe5201372190374886a70207b042294af5bd64ce725cd8dceb344e6d11c09d1aaaf4d660fb26c1f87c13fc1da14997f1b5a71995dff8fbe0a62fae8473c7bdbd05bfb607d",
    },
    {
        "channel_id": None,
        "private_key": "6e1fde9cf9e2359a87420b65a87dc0c66136e66945196ba2475990d8a0c3a25b",
        "challenge": "b05e6b8ad4d69abf74aa3be3c0ee40ae07d66e1895b9ab09285a2f1192d562d2",
        "signature": "7beb282184baadd08f166f16dd683b39cab53816ed81e6955def951cb2ddad1ec184e206746fd82bda075af03711d3d5658fc84a76196b0fa8d1ebc92ef9f30bb05e6b8ad4d69abf74aa3be3c0ee40ae07d66e1895b9ab09285a2f1192d562d2",
    },
    # _WITH_ channel_id
    {
        "channel_id": "62e935ae755f3d48f80d4d59f6121358c435722a67e859cc0caa8b539027f2ff",
        "private_key": "4d57d97a68f555696620a6d849c0ce582568518d729eb753dc7c732de2804510",
        "challenge": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        "signature": "9b6f41540c9b95b4b7b281c3042fa9c54cef43c842d62ea3fd6030fcb66e70b3e80d49d44c29d1635da9348d02ec93f3ed1ef227dfb59a07b580095c2b82f80f9d16ca518aa0c2b707f2b2a609edeca73bca8dd59817a633f35574ac6fd80d00",
    },
    {
        "channel_id": "62e935ae755f3d48f80d4d59f6121358c435722a67e859cc0caa8b539027f2ff",
        "private_key": "d511fe78e23934b3dadb52fcd022974b80bd92bccc7c5cf404e46cc0a8a2f5cd",
        "challenge": "b26c1f87c13fc1da14997f1b5a71995dff8fbe0a62fae8473c7bdbd05bfb607d",
        "signature": "305aaa3ac25e98f651427688b3fc43fe7d8a68a7ec1d7d61c61517c519bd4a427c3015599d83ca28b4c652333920223844ef0725eb5dc2febfd6af7677b73f01d0852a29b460fc92ec943242ac638a053bbacc200512b18b30d15083cbdc9282",
    },
    {
        "channel_id": "62e935ae755f3d48f80d4d59f6121358c435722a67e859cc0caa8b539027f2ff",
        "private_key": "6e1fde9cf9e2359a87420b65a87dc0c66136e66945196ba2475990d8a0c3a25b",
        "challenge": "b05e6b8ad4d69abf74aa3be3c0ee40ae07d66e1895b9ab09285a2f1192d562d2",
        "signature": "ee3c7644fd8070532bc1fde3d70d742267da545d8c8f03e63bda63f1ad4214f4d2c4bfdb4eb9526def42deeb7e31602a6ff99eba893e0a4ad4d45892ca75e608d2b75e24a189a7f78ca776ba36fc53f6c3e31c32f251f2c524f0a44202f2902d",
    },
]


class TestSigVectors(unittest.TestCase):
    def test_vectors(self):
        session = Mock()

        for testvec in test_vectors_1:
            # setup fake transport details including fake channel_id
            if testvec["channel_id"]:
                channel_id = binascii.a2b_hex(testvec["channel_id"])
                channel_id_type = "tls-unique"
                session._transport.transport_details = types.TransportDetails(
                    channel_id={"tls-unique": channel_id}
                )
            else:
                channel_id = None
                channel_id_type = None
                session._transport.transport_details = types.TransportDetails(
                    channel_id=None
                )

            # private signing key (the seed for it)
            private_key = CryptosignKey.from_bytes(
                binascii.a2b_hex(testvec["private_key"])
            )

            # the fake challenge we've received
            challenge = types.Challenge(
                "cryptosign", dict(challenge=testvec["challenge"])
            )

            # ok, now sign the challenge
            f_signed = private_key.sign_challenge(
                challenge, channel_id=channel_id, channel_id_type=channel_id_type
            )

            def success(signed):
                # the signature returned is a Hex encoded string
                self.assertTrue(type(signed) == str)

                # we return the concatenation of the signature and the message signed (96 bytes)
                self.assertEqual(
                    192,
                    len(signed),
                )

                # must match the expected value in our test vector
                self.assertEqual(
                    testvec["signature"],
                    signed,
                )

            def failed(err):
                self.fail(str(err))

            txaio.add_callbacks(f_signed, success, failed)


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.key = CryptosignKey.from_ssh_bytes(keybody)
        self.privkey_hex = self.key._key.encode(encoder=HexEncoder)

        # all tests here fake the use of channel_id_type='tls-unique' with the following channel_id
        m = hashlib.sha256()
        m.update("some TLS message".encode())

        # 62e935ae755f3d48f80d4d59f6121358c435722a67e859cc0caa8b539027f2ff
        channel_id = m.digest()

        self.transport_details = types.TransportDetails(
            channel_id={"tls-unique": channel_id}
        )

    def test_public_key(self):
        self.assertEqual(
            self.key.public_key(binary=False),
            "1adfc8bfe1d35616e64dffbd900096f23b066f914c8c2ffbb66f6075b96e116d",
        )

    def test_valid(self):
        session = Mock()
        session._transport.transport_details = self.transport_details

        challenge = types.Challenge("cryptosign", dict(challenge="ff" * 32))
        f_signed = self.key.sign_challenge(
            challenge,
            channel_id=self.transport_details.channel_id["tls-unique"],
            channel_id_type="tls-unique",
        )

        def success(signed):
            self.assertEqual(
                192,
                len(signed),
            )
            self.assertEqual(
                "9b6f41540c9b95b4b7b281c3042fa9c54cef43c842d62ea3fd6030fcb66e70b3e80d49d44c29d1635da9348d02ec93f3ed1ef227dfb59a07b580095c2b82f80f9d16ca518aa0c2b707f2b2a609edeca73bca8dd59817a633f35574ac6fd80d00",
                signed,
            )

        def failed(err):
            self.fail(str(err))

        txaio.add_callbacks(f_signed, success, failed)

    def test_authenticator(self):
        authenticator = create_authenticator(
            "cryptosign",
            authid="someone",
            authextra={"channel_binding": "tls-unique"},
            privkey=self.privkey_hex,
        )
        session = Mock()
        session._transport.transport_details = self.transport_details
        challenge = types.Challenge("cryptosign", dict(challenge="ff" * 32))
        f_reply = authenticator.on_challenge(session, challenge)

        def success(reply):
            self.assertEqual(
                reply,
                "9b6f41540c9b95b4b7b281c3042fa9c54cef43c842d62ea3fd6030fcb66e70b3e80d49d44c29d1635da9348d02ec93f3ed1ef227dfb59a07b580095c2b82f80f9d16ca518aa0c2b707f2b2a609edeca73bca8dd59817a633f35574ac6fd80d00",
            )

        def failed(err):
            self.fail(str(err))

        txaio.add_callbacks(f_reply, success, failed)


class TestKey(unittest.TestCase):
    def test_pad(self):
        self.assertEqual(_makepad(0), b"")
        self.assertEqual(_makepad(2), b"\x01\x02")
        self.assertEqual(_makepad(3), b"\x01\x02\x03")
        self.assertEqual(
            _makepad(30),
            b"\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e",
        )
        self.assertEqual(
            binascii.b2a_hex(_makepad(30)).decode(),
            "0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e",
        )

    def test_key(self):
        with tempfile.NamedTemporaryFile("w+t") as fp:
            fp.write(keybody)
            fp.seek(0)

            key = CryptosignKey.from_ssh_file(fp.name)
            self.assertEqual(
                key.public_key(),
                "1adfc8bfe1d35616e64dffbd900096f23b066f914c8c2ffbb66f6075b96e116d",
            )

    def test_pubkey(self):
        with tempfile.NamedTemporaryFile("w+t") as fp:
            fp.write(pubkey)
            fp.seek(0)

            key = CryptosignKey.from_ssh_file(fp.name)
            self.assertEqual(
                key.public_key(binary=False),
                "9569de18c7c0843212569dcddf2615c7f46125dc9b2292dea30b07b56a4d02a6",
            )
            self.assertEqual(key.comment, "someuser@example.com")


class TestAuthExtra(unittest.TestCase):
    def test_default_ctor(self):
        ae = CryptosignAuthextra()
        self.assertEqual(ae.marshal(), {})

    def test_ctor(self):
        ae1 = CryptosignAuthextra(pubkey=b"\xff" * 32)
        self.assertEqual(ae1.marshal(), {"pubkey": "ff" * 32})

        ae1 = CryptosignAuthextra(pubkey=b"\xff" * 32, bandwidth=200)
        self.assertEqual(
            ae1.marshal(), {"pubkey": "ff" * 32, "reservation": {"bandwidth": 200}}
        )

    def test_parse(self):
        data_original = {
            "pubkey": "9019a424b040859c108edee02e64c1dcb32b253686d7b5db56c306e9bdb2fe7e",
            "challenge": "fe81c84e94a75a357c259d6b37361e43966a45f57dff181bb61b2f91a0f4ac88",
            "channel_binding": "tls-unique",
            "channel_id": "2e642bf991f48ece9133a0a32d15550921dda12bfebfbc941571d4b2960540bc",
            "trustroot": "0xe78ea2fE1533D4beD9A10d91934e109A130D0ad8",
            "reservation": {
                "chain_id": 999,
                "block_no": 123456789,
                "realm": "0x163D58cE482560B7826b4612f40aa2A7d53310C4",
                "delegate": "0x72b3486d38E9f49215b487CeAaDF27D6acf22115",
                "seeder": "0x52d66f36A7927cF9612e1b40bD6549d08E0513Ff",
                "bandwidth": 200,
            },
            "signature": "747763c69394270603f64af5be3f8256a14b41ff51027e583ee81db9f1f15a01cc8e55218a76139f26dbaaa78d8a537d80d248b3fc6245ecf4602cc5fbb0f6452e",
        }
        ae1 = CryptosignAuthextra.parse(data_original)
        data_marshalled = ae1.marshal()

        # FIXME: marshal check-summed eth addresses
        data_original["trustroot"] = data_original["trustroot"].lower()
        for k in ["realm", "delegate", "seeder"]:
            data_original["reservation"][k] = data_original["reservation"][k].lower()

        self.assertEqual(data_marshalled, data_original)
