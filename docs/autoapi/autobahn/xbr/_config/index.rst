:mod:`autobahn.xbr._config`
===========================

.. py:module:: autobahn.xbr._config


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.xbr._config.Profile
   autobahn.xbr._config.UserConfig
   autobahn.xbr._config.WampUrl
   autobahn.xbr._config.EthereumAddress
   autobahn.xbr._config.PrivateKey



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.xbr._config.style_error
   autobahn.xbr._config.style_ok
   autobahn.xbr._config.prompt_for_wamp_url
   autobahn.xbr._config.prompt_for_ethereum_address
   autobahn.xbr._config.prompt_for_key
   autobahn.xbr._config.load_or_create_profile


.. data:: _HAS_COLOR_TERM
   :annotation: = False

   

.. data:: term
   

   

.. class:: Profile(path=None, name=None, ethkey=None, cskey=None, username=None, email=None, network_url=None, network_realm=None, market_url=None, market_realm=None, infura_url=None, infura_network=None, infura_key=None, infura_secret=None)


   Bases: :class:`object`

   .. method:: parse(path, name, items)
      :staticmethod:



.. class:: UserConfig(config_path)


   Bases: :class:`object`


.. data:: _DEFAULT_CFC_URL
   

   

.. function:: style_error(text)


.. function:: style_ok(text)


.. class:: WampUrl


   Bases: :class:`click.ParamType`

   WAMP transport URL validator.

   .. attribute:: name
      :annotation: = WAMP transport URL

      

   .. method:: convert(self, value, param, ctx)

      Converts the value.  This is not invoked for values that are
      `None` (the missing value).



.. function:: prompt_for_wamp_url(msg, default=None)

   Prompt user for WAMP transport URL (eg "wss://planet.xbr.network/ws").


.. class:: EthereumAddress


   Bases: :class:`click.ParamType`

   Ethereum address validator.

   .. attribute:: name
      :annotation: = Ethereum address

      

   .. method:: convert(self, value, param, ctx)

      Converts the value.  This is not invoked for values that are
      `None` (the missing value).



.. function:: prompt_for_ethereum_address(msg)

   Prompt user for an Ethereum (public) address.


.. class:: PrivateKey(key_len)


   Bases: :class:`click.ParamType`

   Private key (32 bytes in HEX) validator.

   .. attribute:: name
      :annotation: = Private key

      

   .. method:: convert(self, value, param, ctx)

      Converts the value.  This is not invoked for values that are
      `None` (the missing value).



.. function:: prompt_for_key(msg, key_len, default=None)

   Prompt user for a binary key of given length (in HEX).


.. data:: _DEFAULT_CONFIG
   :annotation: = [default]
# username used with this profile
username={username}

# user email used with the profile (e.g. for verification emails)
email={email}

# XBR network node used as a directory server and gateway to XBR smart contracts
network_url={network_url}

# WAMP realm on network node, usually "xbrnetwork"
network_realm={network_realm}

# user private WAMP-cryptosign key (for client authentication)
cskey={cskey}

# user private Ethereum key (for signing transactions and e2e data encryption)
ethkey={ethkey}


   

.. function:: load_or_create_profile(dotdir=None, profile=None, default_url=None, default_realm=None, default_email=None, default_username=None)


