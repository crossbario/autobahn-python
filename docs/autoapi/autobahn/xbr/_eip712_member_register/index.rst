:mod:`autobahn.xbr._eip712_member_register`
===========================================

.. py:module:: autobahn.xbr._eip712_member_register


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._eip712_member_register._create_eip712_member_register
   autobahn.xbr._eip712_member_register.sign_eip712_member_register
   autobahn.xbr._eip712_member_register.recover_eip712_member_register


.. function:: _create_eip712_member_register(chainId: int, verifyingContract: bytes, member: bytes, registered: int, eula: str, profile: Optional[str]) -> dict

   :param chainId:
   :param verifyingContract:
   :param member:
   :param registered:
   :param eula:
   :param profile:
   :return:


.. function:: sign_eip712_member_register(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes, registered: int, eula: Optional[str], profile: str) -> bytes

   :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
   :type eth_privkey: bytes

   :return: The signature according to EIP712 (32+32+1 raw bytes).
   :rtype: bytes


.. function:: recover_eip712_member_register(chainId: int, verifyingContract: bytes, member: bytes, registered: int, eula: str, profile: Optional[str], signature: bytes) -> bytes

   Recover the signer address the given EIP712 signature was signed with.

   :return: The (computed) signer address the signature was signed with.
   :rtype: bytes


