:mod:`autobahn.xbr._eip712_member_unregister`
=============================================

.. py:module:: autobahn.xbr._eip712_member_unregister


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._eip712_member_unregister._create_eip712_member_unregister
   autobahn.xbr._eip712_member_unregister.sign_eip712_member_unregister
   autobahn.xbr._eip712_member_unregister.recover_eip712_member_unregister


.. function:: _create_eip712_member_unregister(chainId: int, verifyingContract: bytes, member: bytes, retired: int) -> dict

   :param chainId:
   :param verifyingContract:
   :param member:
   :param retired:
   :return:


.. function:: sign_eip712_member_unregister(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes, retired: int) -> bytes

   :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
   :type eth_privkey: bytes

   :return: The signature according to EIP712 (32+32+1 raw bytes).
   :rtype: bytes


.. function:: recover_eip712_member_unregister(chainId: int, verifyingContract: bytes, member: bytes, retired: int, signature: bytes) -> bytes

   Recover the signer address the given EIP712 signature was signed with.

   :return: The (computed) signer address the signature was signed with.
   :rtype: bytes


