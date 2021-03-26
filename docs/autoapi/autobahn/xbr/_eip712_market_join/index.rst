:mod:`autobahn.xbr._eip712_market_join`
=======================================

.. py:module:: autobahn.xbr._eip712_market_join


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._eip712_market_join._create_eip712_market_join
   autobahn.xbr._eip712_market_join.sign_eip712_market_join
   autobahn.xbr._eip712_market_join.recover_eip712_market_join


.. function:: _create_eip712_market_join(chainId: int, verifyingContract: bytes, member: bytes, joined: int, marketId: bytes, actorType: int, meta: Optional[str]) -> dict

   :param chainId:
   :param verifyingContract:
   :param member:
   :param joined:
   :param marketId:
   :param actorType:
   :param meta:
   :return:


.. function:: sign_eip712_market_join(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes, joined: int, marketId: bytes, actorType: int, meta: str) -> bytes

   :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
   :type eth_privkey: bytes

   :return: The signature according to EIP712 (32+32+1 raw bytes).
   :rtype: bytes


.. function:: recover_eip712_market_join(chainId: int, verifyingContract: bytes, member: bytes, joined: int, marketId: bytes, actorType: int, meta: str, signature: bytes) -> bytes

   Recover the signer address the given EIP712 signature was signed with.

   :return: The (computed) signer address the signature was signed with.
   :rtype: bytes


