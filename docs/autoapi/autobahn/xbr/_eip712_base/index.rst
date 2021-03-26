:mod:`autobahn.xbr._eip712_base`
================================

.. py:module:: autobahn.xbr._eip712_base


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._eip712_base.sign
   autobahn.xbr._eip712_base.recover
   autobahn.xbr._eip712_base.is_address
   autobahn.xbr._eip712_base.is_bytes16
   autobahn.xbr._eip712_base.is_signature
   autobahn.xbr._eip712_base.is_eth_privkey
   autobahn.xbr._eip712_base.is_cs_pubkey
   autobahn.xbr._eip712_base.is_block_number
   autobahn.xbr._eip712_base.is_chain_id


.. data:: _EIP712_SIG_LEN
   

   

.. function:: sign(eth_privkey, data)

   Sign the given data using the given Ethereum private key.

   :param eth_privkey: Signing key.
   :param data: Data to sign.
   :return: Signature.


.. function:: recover(data, signature)

   Recover the Ethereum address of the signer, given the data and signature.

   :param data: Signed data.
   :param signature: Signature.
   :return: Signing address.


.. function:: is_address(provided)

   Check if the value is a proper Ethereum address.

   :param provided: The value to check.
   :return: True iff the value is of correct type.


.. function:: is_bytes16(provided)

   Check if the value is a proper (binary) UUID.

   :param provided: The value to check.
   :return: True iff the value is of correct type.


.. function:: is_signature(provided)

   Check if the value is a proper Ethereum signature.

   :param provided: The value to check.
   :return: True iff the value is of correct type.


.. function:: is_eth_privkey(provided)

   Check if the value is a proper WAMP-cryptosign private key.

   :param provided: The value to check.
   :return: True iff the value is of correct type.


.. function:: is_cs_pubkey(provided)

   Check if the value is a proper WAMP-cryptosign public key.

   :param provided: The value to check.
   :return: True iff the value is of correct type.


.. function:: is_block_number(provided)

   Check if the value is a proper Ethereum block number.

   :param provided: The value to check.
   :return: True iff the value is of correct type.


.. function:: is_chain_id(provided)

   Check if the value is a proper Ethereum chain ID.

   :param provided: The value to check.
   :return: True iff the value is of correct type.


