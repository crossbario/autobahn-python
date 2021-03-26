:mod:`autobahn.xbr._eip712_consent`
===================================

.. py:module:: autobahn.xbr._eip712_consent


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._eip712_consent._create_eip712_consent
   autobahn.xbr._eip712_consent.sign_eip712_consent
   autobahn.xbr._eip712_consent.recover_eip712_consent


.. function:: _create_eip712_consent(chainId: int, verifyingContract: bytes, member: bytes, updated: int, marketId: bytes, delegate: bytes, delegateType: int, apiCatalog: bytes, consent: bool, servicePrefix: Optional[str]) -> dict

   :param chainId:
   :param verifyingContract:
   :param member:
   :param updated:
   :param marketId:
   :param delegate:
   :param delegateType:
   :param apiCatalog:
   :param consent:
   :param servicePrefix:
   :return:


.. function:: sign_eip712_consent(eth_privkey: bytes, chainId: int, verifyingContract: bytes, member: bytes, updated: int, marketId: bytes, delegate: bytes, delegateType: int, apiCatalog: bytes, consent: bool, servicePrefix: str) -> bytes

   :param eth_privkey: Ethereum address of buyer (a raw 20 bytes Ethereum address).
   :type eth_privkey: bytes

   :return: The signature according to EIP712 (32+32+1 raw bytes).
   :rtype: bytes


.. function:: recover_eip712_consent(chainId: int, verifyingContract: bytes, member: bytes, updated: int, marketId: bytes, delegate: bytes, delegateType: int, apiCatalog: bytes, consent: bool, servicePrefix: str, signature: bytes) -> bytes

   Recover the signer address the given EIP712 signature was signed with.

   :return: The (computed) signer address the signature was signed with.
   :rtype: bytes


