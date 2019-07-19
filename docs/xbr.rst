XBR Programming
===============

This is the **XBR Lib for Python** API reference documentation, generated from the Python source code
using `Sphinx <http://www.sphinx-doc.org>`_.

.. contents:: :local:

----------

On-chain XBR smart contracts
----------------------------

The root anchor of the XBR network is a set of smart contracts on the Ethereum blockchain. The contracts
are written in Solidity and published as open-source `on GitHub <https://github.com/crossbario/xbr-protocol>`_.

To talk to the XBR smart contracts on the blockchain, you need two things:

1. the addresses and
2. the ABI files (JSON)

of the XBR smart contracts. Both of which are built into the Autobahn library.


SimpleBlockchain
................

While you *can* use just the raw addresses and ABI blobs contained in Autobahn, and use whatever
way and form to talk directly to the blockchain fully on your own, Autobahn *also* provides a convenient
blockchain client with specific functions directly supporting XBR:

.. autoclass:: autobahn.xbr.SimpleBlockchain
    :members:
        start,
        stop,
        get_balances,
        get_contract_adrs


Using the ABI files
...................

To directly use the embedded ABI files:

.. code-block:: python

    import json
    import pkg_resources
    from pprint import pprint

    with open(pkg_resources.resource_filename('xbr', 'contracts/XBRToken.json')) as f:
        data = json.loads(f.read())
        abi = data['abi']
        pprint(abi)


Off-chain XBR market maker
--------------------------

SimpleBuyer
...........

Autobahn includes a "simple buyer" for use in buyer delegate user services which is able
to automatically quote and buy data encryption keys via the market maker from sellers
in a market.

The simple buyer operates in the background and automatically buys keys on demand, as the
user calls "unwrap(ciphertext)" on received XBR encrypted application payload:

.. autoclass:: autobahn.xbr.SimpleBuyer
    :members:
        start,
        stop,
        balance,
        open_channel,
        close_channel,
        unwrap


SimpleSeller
............

Autobahn includes a "simple seller" for use in seller delegate user services which is able
to automatically offer and sell data encryption keys via the market maker to buyers
in a market.

.. autoclass:: autobahn.xbr.SimpleSeller
    :members:
        start,
        stop,
        wrap,
        sell,
        public_key,
        add


KeySeries
.........

Helper class used in SimpleSeller to create an auto-rotating (time-interval based)
data encryption key series:

.. autoclass:: autobahn.xbr.KeySeries
    :members:
        key_id,
        encrypt,
        encrypt_key,
        start,
        stop


Interface Reference
-------------------

IMarketMaker
............

.. autoclass:: autobahn.xbr.IMarketMaker
    :members:
        status,
        offer,
        revoke,
        quote,
        buy,
        get_payment_channels,
        get_payment_channel


IProvider
.........

.. autoclass:: autobahn.xbr.IProvider
    :members:
        sell


IConsumer
.........

.. autoclass:: autobahn.xbr.IConsumer
    :members:


ISeller
.......

.. autoclass:: autobahn.xbr.ISeller
    :members:
        start,
        wrap


IBuyer
......

.. autoclass:: autobahn.xbr.IBuyer
    :members:
        start,
        unwrap
