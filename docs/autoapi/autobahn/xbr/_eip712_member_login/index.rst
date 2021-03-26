:mod:`autobahn.xbr._eip712_member_login`
========================================

.. py:module:: autobahn.xbr._eip712_member_login


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._eip712_member_login._create_eip712_member_login
   autobahn.xbr._eip712_member_login.sign_eip712_member_login
   autobahn.xbr._eip712_member_login.recover_eip712_member_login


.. function:: _create_eip712_member_login(chainId: int, verifyingContract: bytes, member: bytes, loggedIn: int, timestamp: int, member_email: str, client_pubkey: bytes) -> dict

   :param chainId:
   :param blockNumber:
   :param verifyingContract:
   :param member:
   :param timestamp:
   :param member_email:
   :param client_pubkey:
   :return:


.. function:: sign_eip712_member_login(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes, loggedIn: int, timestamp: int, member_email: str, client_pubkey: bytes) -> bytes

   :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
   :type eth_privkey: bytes

   :return: The signature according to EIP712 (32+32+1 raw bytes).
   :rtype: bytes


.. function:: recover_eip712_member_login(chainId: int, verifyingContract: bytes, member: bytes, loggedIn: int, timestamp: int, member_email: str, client_pubkey: bytes, signature: bytes) -> bytes

   Recover the signer address the given EIP712 signature was signed with.

   :return: The (computed) signer address the signature was signed with.
   :rtype: bytes


