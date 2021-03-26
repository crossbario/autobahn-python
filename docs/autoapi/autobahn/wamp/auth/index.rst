:mod:`autobahn.wamp.auth`
=========================

.. py:module:: autobahn.wamp.auth


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.auth.AuthAnonymous
   autobahn.wamp.auth.AuthTicket
   autobahn.wamp.auth.AuthCryptoSign
   autobahn.wamp.auth.AuthScram
   autobahn.wamp.auth.AuthWampCra



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.wamp.auth.create_authenticator
   autobahn.wamp.auth.generate_totp_secret
   autobahn.wamp.auth.compute_totp
   autobahn.wamp.auth.check_totp
   autobahn.wamp.auth.qrcode_from_totp
   autobahn.wamp.auth.pbkdf2
   autobahn.wamp.auth.derive_key
   autobahn.wamp.auth.generate_wcs
   autobahn.wamp.auth.compute_wcs
   autobahn.wamp.auth.derive_scram_credential


.. function:: create_authenticator(name, **kwargs)

   Accepts various keys and values to configure an authenticator. The
   valid keys depend on the kind of authenticator but all can
   understand: `authextra`, `authid` and `authrole`

   :return: an instance implementing IAuthenticator with the given
       configuration.


.. class:: AuthAnonymous(**kw)


   Bases: :class:`object`

   .. attribute:: name
      :annotation: = anonymous

      

   .. method:: authextra(self)
      :property:


   .. method:: on_challenge(self, session, challenge)


   .. method:: on_welcome(self, msg, authextra)



.. class:: AuthTicket(**kw)


   Bases: :class:`object`

   .. attribute:: name
      :annotation: = ticket

      

   .. method:: authextra(self)
      :property:


   .. method:: on_challenge(self, session, challenge)


   .. method:: on_welcome(self, msg, authextra)



.. class:: AuthCryptoSign(**kw)


   Bases: :class:`object`

   .. attribute:: name
      :annotation: = cryptosign

      

   .. method:: authextra(self)
      :property:


   .. method:: on_challenge(self, session, challenge)


   .. method:: on_welcome(self, msg, authextra)



.. class:: AuthScram(**kw)


   Bases: :class:`object`

   Implements "wamp-scram" authentication for components.

   NOTE: This is a prototype of a draft spec; see
   https://github.com/wamp-proto/wamp-proto/issues/135

   .. attribute:: name
      :annotation: = scram

      

   .. method:: authextra(self)
      :property:


   .. method:: on_challenge(self, session, challenge)


   .. method:: on_welcome(self, session, authextra)

      When the server is satisfied, it sends a 'WELCOME' message.

      This hook allows us an opportunity to deny the session right
      before it gets set up -- we check the server-signature thus
      authorizing the server and if it fails we drop the connection.



.. class:: AuthWampCra(**kw)


   Bases: :class:`object`

   .. attribute:: name
      :annotation: = wampcra

      

   .. method:: authextra(self)
      :property:


   .. method:: on_challenge(self, session, challenge)


   .. method:: on_welcome(self, msg, authextra)



.. function:: generate_totp_secret(length=10)

   Generates a new Base32 encoded, random secret.

   .. seealso:: http://en.wikipedia.org/wiki/Base32

   :param length: The length of the entropy used to generate the secret.
   :type length: int

   :returns: The generated secret in Base32 (letters ``A-Z`` and digits ``2-7``).
      The length of the generated secret is ``length * 8 / 5`` octets.
   :rtype: unicode


.. function:: compute_totp(secret, offset=0)

   Computes the current TOTP code.

   :param secret: Base32 encoded secret.
   :type secret: unicode
   :param offset: Time offset (in steps, use eg -1, 0, +1 for compliance with RFC6238)
       for which to compute TOTP.
   :type offset: int

   :returns: TOTP for current time (+/- offset).
   :rtype: unicode


.. function:: check_totp(secret, ticket)

   Check a TOTP value received from a principal trying to authenticate against
   the expected value computed from the secret shared between the principal and
   the authenticating entity.

   The Internet can be slow, and clocks might not match exactly, so some
   leniency is allowed. RFC6238 recommends looking an extra time step in either
   direction, which essentially opens the window from 30 seconds to 90 seconds.

   :param secret: The secret shared between the principal (eg a client) that
       is authenticating, and the authenticating entity (eg a server).
   :type secret: unicode
   :param ticket: The TOTP value to be checked.
   :type ticket: unicode

   :returns: ``True`` if the TOTP value is correct, else ``False``.
   :rtype: bool


.. function:: qrcode_from_totp(secret, label, issuer)


.. function:: pbkdf2(data, salt, iterations=1000, keylen=32, hashfunc=None)

   Returns a binary digest for the PBKDF2 hash algorithm of ``data``
   with the given ``salt``. It iterates ``iterations`` time and produces a
   key of ``keylen`` bytes. By default SHA-256 is used as hash function,
   a different hashlib ``hashfunc`` can be provided.

   :param data: The data for which to compute the PBKDF2 derived key.
   :type data: bytes
   :param salt: The salt to use for deriving the key.
   :type salt: bytes
   :param iterations: The number of iterations to perform in PBKDF2.
   :type iterations: int
   :param keylen: The length of the cryptographic key to derive.
   :type keylen: int
   :param hashfunc: Name of the hash algorithm to use
   :type hashfunc: str

   :returns: The derived cryptographic key.
   :rtype: bytes


.. function:: derive_key(secret, salt, iterations=1000, keylen=32)

   Computes a derived cryptographic key from a password according to PBKDF2.

   .. seealso:: http://en.wikipedia.org/wiki/PBKDF2

   :param secret: The secret.
   :type secret: bytes or unicode
   :param salt: The salt to be used.
   :type salt: bytes or unicode
   :param iterations: Number of iterations of derivation algorithm to run.
   :type iterations: int
   :param keylen: Length of the key to derive in bytes.
   :type keylen: int

   :return: The derived key in Base64 encoding.
   :rtype: bytes


.. function:: generate_wcs(length=14)

   Generates a new random secret for use with WAMP-CRA.

   The secret generated is a random character sequence drawn from

   - upper and lower case latin letters
   - digits
   -

   :param length: The length of the secret to generate.
   :type length: int

   :return: The generated secret. The length of the generated is ``length`` octets.
   :rtype: bytes


.. function:: compute_wcs(key, challenge)

   Compute an WAMP-CRA authentication signature from an authentication
   challenge and a (derived) key.

   :param key: The key derived (via PBKDF2) from the secret.
   :type key: bytes
   :param challenge: The authentication challenge to sign.
   :type challenge: bytes

   :return: The authentication signature.
   :rtype: bytes


.. function:: derive_scram_credential(email: str, password: str, salt: Optional[bytes] = None) -> Dict

   Derive WAMP-SCRAM credentials from user email and password. The SCRAM parameters used
   are the following (these are also contained in the returned credentials):

   * kdf ``argon2id-13``
   * time cost ``4096``
   * memory cost ``512``
   * parallelism ``1``

   See `draft-irtf-cfrg-argon2 <https://datatracker.ietf.org/doc/draft-irtf-cfrg-argon2/>`__ and
   `argon2-cffi <https://argon2-cffi.readthedocs.io/en/stable/>`__.

   :param email: User email.
   :param password: User password.
   :param salt: Optional salt to use (must be 16 bytes long). If none is given, compute salt
       from email as ``salt = SHA256(email)[:16]``.
   :return: WAMP-SCRAM credentials. When serialized, the returned credentials can be copy-pasted
       into the ``config.json`` node configuration for a Crossbar.io node.


