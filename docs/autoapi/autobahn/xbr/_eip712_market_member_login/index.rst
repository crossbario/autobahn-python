:mod:`autobahn.xbr._eip712_market_member_login`
===============================================

.. py:module:: autobahn.xbr._eip712_market_member_login


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._eip712_market_member_login._create_eip712_market_member_login
   autobahn.xbr._eip712_market_member_login.sign_eip712_market_member_login
   autobahn.xbr._eip712_market_member_login.recover_eip712_market_member_login


.. function:: _create_eip712_market_member_login(member: bytes, client_pubkey: bytes) -> dict


.. function:: sign_eip712_market_member_login(eth_privkey: bytes, member: bytes, client_pubkey: bytes) -> bytes


.. function:: recover_eip712_market_member_login(member: bytes, client_pubkey: bytes, signature: bytes) -> bytes


