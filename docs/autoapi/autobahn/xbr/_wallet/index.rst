:mod:`autobahn.xbr._wallet`
===========================

.. py:module:: autobahn.xbr._wallet


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._wallet.stretch_argon2_secret
   autobahn.xbr._wallet.expand_argon2_secret
   autobahn.xbr._wallet.pkm_from_argon2_secret


.. function:: stretch_argon2_secret(email: str, password: str, salt: Optional[bytes] = None) -> bytes

   Compute argon2id based secret from user email and password only. This uses Argon2id
   for stretching a potentially weak user password/PIN and subsequent HKDF based key
   extending to derive private key material (PKM) for different usage contexts.

   The Argon2 parameters used are the following:

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
   :return: The computed private key material (256b, 32 octets).


.. function:: expand_argon2_secret(pkm: bytes, context: bytes, salt: Optional[bytes] = None) -> bytes

   Expand ``pkm`` and ``context`` into a key of length ``bytes`` using
   HKDF's expand function based on HMAC SHA-512). See the HKDF draft RFC and paper for usage notes.

   :param pkm:
   :param context:
   :param salt:
   :return:


.. function:: pkm_from_argon2_secret(email: str, password: str, context: str, salt: Optional[bytes] = None) -> bytes

   :param email:
   :param password:
   :param context:
   :param salt:
   :return:


