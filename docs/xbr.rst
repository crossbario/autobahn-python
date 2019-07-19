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

SimpleBuyer Example
...................

Here is a complete example buyer:

.. code-block:: python

    import binascii
    import os

    from autobahn.twisted.component import Component, run
    from autobahn.xbr import SimpleBuyer
    from autobahn.wamp.types import SubscribeOptions

    comp = Component(
        transports=os.environ.get('XBR_INSTANCE', 'wss://continental2.crossbario.com/ws'),
        realm=os.environ.get('XBR_REALM', 'realm1'),
        extra={
            'market_maker_adr': os.environ.get('XBR_MARKET_MAKER_ADR',
                '0xff035c911accf7c7154c51cb62460b50f43ea54f'),
            'buyer_privkey': os.environ.get('XBR_BUYER_PRIVKEY',
                '646f1ce2fdad0e6deeeb5c7e8e5543bdde65e86029e2fd9fc169899c440a7913'),
        }
    )


    @comp.on_join
    async def joined(session, details):
        print('Buyer session joined', details)

        market_maker_adr = binascii.a2b_hex(session.config.extra['market_maker_adr'][2:])
        print('Using market maker adr:', session.config.extra['market_maker_adr'])

        buyer_privkey = binascii.a2b_hex(session.config.extra['buyer_privkey'])

        buyer = SimpleBuyer(market_maker_adr, buyer_privkey, 100)
        balance = await buyer.start(session, details.authid)
        print("Remaining balance={}".format(balance))

        async def on_event(key_id, enc_ser, ciphertext, details=None):
            payload = await buyer.unwrap(key_id, enc_ser, ciphertext)
            print('Received event {}:'.format(details.publication), payload)

        await session.subscribe(on_event, "io.crossbar.example",
            options=SubscribeOptions(details=True))


    if __name__ == '__main__':
        run([comp])


SimpleSeller
............

Autobahn includes a "simple seller" for use in seller delegate user services which is able
to automatically offer and sell data encryption keys via the market maker to buyers
in a market:

.. autoclass:: autobahn.xbr.SimpleSeller
    :members:
        start,
        stop,
        wrap,
        sell,
        public_key,
        add

SimpleSeller Example
....................

Here is a complete example seller:

.. code-block:: python

    import binascii
    import os
    from time import sleep
    from uuid import UUID

    from autobahn.twisted.component import Component, run
    from autobahn.twisted.util import sleep
    from autobahn.wamp.types import PublishOptions
    from autobahn.xbr import SimpleSeller

    comp = Component(
        transports=os.environ.get('XBR_INSTANCE', 'wss://continental2.crossbario.com/ws'),
        realm=os.environ.get('XBR_REALM', 'realm1'),
        extra={
            'market_maker_adr': os.environ.get('XBR_MARKET_MAKER_ADR',
                '0xff035c911accf7c7154c51cb62460b50f43ea54f'),
            'seller_privkey': os.environ.get('XBR_SELLER_PRIVKEY',
                '646f1ce2fdad0e6deeeb5c7e8e5543bdde65e86029e2fd9fc169899c440a7913'),
        }
    )

    running = False


    @comp.on_join
    async def joined(session, details):
        print('Seller session joined', details)
        global running
        running = True

        market_maker_adr = binascii.a2b_hex(session.config.extra['market_maker_adr'][2:])
        print('Using market maker adr:', session.config.extra['market_maker_adr'])

        seller_privkey = binascii.a2b_hex(session.config.extra['seller_privkey'])

        api_id = UUID('627f1b5c-58c2-43b1-8422-a34f7d3f5a04').bytes
        topic = 'io.crossbar.example'
        counter = 1

        seller = SimpleSeller(market_maker_adr, seller_privkey)
        seller.add(api_id, topic, 35, 10, None)
        await seller.start(session)

        print('Seller has started')

        while running:
            payload = {'data': 'py-seller', 'counter': counter}
            key_id, enc_ser, ciphertext = await seller.wrap(api_id,
                                                            topic,
                                                            payload)
            pub = await session.publish(topic, key_id, enc_ser, ciphertext,
                                        options=PublishOptions(acknowledge=True))

            print('Published event {}: {}'.format(pub.id, payload))

            counter += 1
            await sleep(1)


    @comp.on_leave
    def left(session, details):
        print('Seller session left', details)
        global running
        running = False


    if __name__ == '__main__':
        run([comp])


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
