XBR Authentication
==================

Overview
--------
.. thumbnail:: _static/wamp-xbr-auth.png

Argon2
------

The following helpers allow a user to maintain a set of private key materials
based on a potentially weak (locking) password (or PIN), and is based on
`Argon2id <https://en.wikipedia.org/wiki/Argon2>`__ and
`HKDF <https://en.wikipedia.org/wiki/HKDF>`__:

* :meth:`stretch_argon2_secret <autobahn.xbr.stretch_argon2_secret>`
* :meth:`expand_argon2_secret <autobahn.xbr.expand_argon2_secret>`
* :meth:`pkm_from_argon2_secret <autobahn.xbr.pkm_from_argon2_secret>`

TOTP
----

* :meth:`generate_totp_secret <autobahn.wamp.auth.generate_totp_secret>`
* :meth:`compute_totp <autobahn.wamp.auth.compute_totp>`
* :meth:`check_totp <autobahn.wamp.auth.check_totp>`
* :meth:`qrcode_from_totp <autobahn.wamp.auth.qrcode_from_totp>`

Verification Code
-----------------

* :meth:`generate_token <autobahn.util.generate_token>`

SPAKE2
------

Write me.

WAMP-Cryptosign
---------------

The following helpers allow WAMP clients to authenticate using WAMP-cryptosign
which is based on Ed25519:

* :class:`AuthCryptoSign <autobahn.wamp.auth.AuthCryptoSign>`
* :class:`SigningKey <autobahn.wamp.cryptosign.SigningKey>`

WAMP-XBR
--------

The following helpers allow WAMP clients to use end-to-end encrypted application
payloads and data-encryption-key exchange transactions signed using an Ethereum
private key, and anchored on-chain (indirectly via a off-chain state channel):

* :meth:`generate_seedphrase <autobahn.xbr.generate_seedphrase>`
* :meth:`check_seedphrase <autobahn.xbr.check_seedphrase>`
* :meth:`account_from_seedphrase <autobahn.xbr.account_from_seedphrase>`

See `BIP39 <https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki>`__
and `Python-BIP39 <https://github.com/trezor/python-mnemonic>`__.
