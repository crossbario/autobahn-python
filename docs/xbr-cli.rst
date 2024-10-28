XBR Command line interface
==========================

Autobahn includes a command-line interface for the `XBR network <https://xbr.network>`__.

Status
------

* ``version``
* ``get-member``
* ``get-market``
* ``get-actor``


* ``register-member``
* ``register-member-verify``
* ``join-market``
* ``join-market-verify``
* ``create-market``
* ``create-market-verify``
* ``open-channel``
* ``get-channel``


Prerequisites
-------------

Installation
............

The XBR CLI (included in the `xbr` install flavor of Autobahn) can be installed using pip:

.. code-block:: console

    $ pip install autobahn[all]

To run the CLI and check for the installed version including on-chain XBR contract addresses in use:

.. code-block:: console

    $ xbrnetwork version

    XBR CLI v20.6.1

    Profile default loaded from /home/oberstet/.xbrnetwork/config.ini

    Contract addresses:

        XBRToken   : 0xaCef957D54c639575f4DB68b1992B36504f33FEA [source: builtin]
        XBRNetwork : 0x7A3d22c59e8F8f1b88ba7205f3f5a65Bc86D04Bc [source: builtin]
        XBRDomain  : 0xf5fb56886f033855C1a36F651E927551749361bC [source: builtin]
        XBRCatalog : 0x2C77E46Ea9502B363343e8c826c41c7fdb25Db66 [source: builtin]
        XBRMarket  : 0x0DcF924ab0846101d31514E9fb3adf5070d4B83d [source: builtin]
        XBRChannel : 0x670497A012322B99a5C18B8463940996141Cb952 [source: builtin]

Help
....

To get help on the available top-level commands:

.. code-block:: console

    $ xbrnetwork --help

    usage: xbrnetwork [-h] [-d] [--url URL] [--realm REALM] [--ethkey ETHKEY] [--cskey CSKEY] [--username USERNAME] [--email EMAIL]
                    [--market MARKET] [--market_title MARKET_TITLE] [--market_label MARKET_LABEL] [--market_homepage MARKET_HOMEPAGE]
                    [--provider_security PROVIDER_SECURITY] [--consumer_security CONSUMER_SECURITY] [--market_fee MARKET_FEE]
                    [--marketmaker MARKETMAKER] [--actor_type {1,2,3}] [--vcode VCODE] [--vaction VACTION] [--channel CHANNEL]
                    [--channel_type {1,2}] [--delegate DELEGATE] [--amount AMOUNT]
                    {get-member,register-member,register-member-verify,get-market,create-market,create-market-verify,get-actor,join-market,join-market-verify,get-channel,open-channel,close-channel}

    positional arguments:
    {get-member,register-member,register-member-verify,get-market,create-market,create-market-verify,get-actor,join-market,join-market-verify,get-channel,open-channel,close-channel}
                            Command to run

    optional arguments:
    -h, --help            show this help message and exit
    -d, --debug           Enable debug output.
    --url URL             The router URL (default: "wss://planet.xbr.network/ws").
    --realm REALM         The realm to join (default: "xbrnetwork").
    --ethkey ETHKEY       Private Ethereum key (32 bytes as HEX encoded string)
    --cskey CSKEY         Private WAMP-cryptosign authentication key (32 bytes as HEX encoded string)
    --username USERNAME   For on-boarding, the new member username.
    --email EMAIL         For on-boarding, the new member email address.
    --market MARKET       For creating new markets, the market UUID.
    --market_title MARKET_TITLE
                            For creating new markets, the market title.
    --market_label MARKET_LABEL
                            For creating new markets, the market label.
    --market_homepage MARKET_HOMEPAGE
                            For creating new markets, the market homepage.
    --provider_security PROVIDER_SECURITY
    --consumer_security CONSUMER_SECURITY
    --market_fee MARKET_FEE
    --marketmaker MARKETMAKER
                            For creating new markets, the market maker address.
    --actor_type {1,2,3}  Actor type: PROVIDER = 1, CONSUMER = 2, PROVIDER_CONSUMER (both) = 3
    --vcode VCODE         For verifications of actions, the verification UUID.
    --vaction VACTION     For verifications of actions (on-board, create-market, ..), the verification code.
    --channel CHANNEL     For creating new channel, the channel UUID.
    --channel_type {1,2}  Channel type: Seller (PAYING) = 1, Buyer (PAYMENT) = 2
    --delegate DELEGATE   For creating new channel, the delegate address.
    --amount AMOUNT       Amount to open the channel with. In tokens of the market coin type, used as means of payment in the market of
                            the channel.

Crypto Wallet
.............

XBR is based on the `Ethereum blockchain <https://ethereum.org/>`__, and all XBR data markets, market operators
and actors (buyers & sellers) in markets are registered on the Ethereum blockchain.

.. note::

    Currently, XBR is still in alpha, and the latest version is XBR v20.5.1 deployed on Rinkeby testnet.
    XBR will be deployed on mainnet with the official stable release.

Market operators and market actors (buyers & sellers) maintain their (potentially anonymous) identity
via crypto wallets where the private wallet key is under exclusive access to the operator or actor.

Running your own crypto wallet is easy using `MetaMask <https://metamask.io/>`__, a browser plugin that runs
in Chrome and Firefox.

First step is to install MetaMask, creating a new wallet:

.. thumbnail:: _static/screenshots/xbr-metamask-1.png

and connect to `Rinkeby testnet <https://www.rinkeby.io/>`__:

.. thumbnail:: _static/screenshots/xbr-metamask-2.png

Then, to use your Ethereum private key with the XBR CLI, export the private key:

.. thumbnail:: _static/screenshots/xbr-metamask-3.png

When using the XBR CLI, you can provide your Ethereum private key using the command line argument ``--ethkey=0x``
appended with your key:

.. code-block:: console

    --ethkey=0x4C1F...

You can also persistently store your Ethereum private key in the CLI configuration file for one of the user
profiles you have there:

.. code-block:: console

    $ cat ${HOME}/.xbrnetwork/config.ini
    [default]

    # user private Ethereum key
    ethkey=0x4C1F...

.. note::

    Obviously, you must protect your *private key*! The *public address* of your wallet is not security
    sensitive. Even the public address however should always be treated carefully regarding privacy. When you
    store your private key in the CLI configuration file, make sure to protect this file using
    ``chmod 600 ${HOME}/.xbrnetwork/config.ini``.

Finally, for testing on Rinkeby, get yourself some Ether from the `Rinkeby faucet <https://faucet.rinkeby.io/>`__:

.. thumbnail:: _static/screenshots/rinkeby-faucet.png

If you want to use the accounts from your MetaMask wallet derived from your wallet's seedphrase, you can
use a helper included with Autobahn to derive private keys for all accounts, eg account `0`:

.. code-block:: console

    >>> from autobahn.xbr import account_from_seedphrase
    >>> acct = account_from_seedphrase('myth like bonus scare over problem client lizard pioneer submit female collect', 0)
    >>> acct.address
    '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'
    >>> acct.privateKey.hex()
    '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    >>>


Client Key
..........

To connect to the XBR Network using the XBR CLI, the client (which connects via WAMP) needs a client private
key (used for WAMP-cryptosign authentication).

A new key can be created by generating 32 random bytes:

.. code-block:: console

    $ openssl rand -hex 32
    ecdc5e97...

When using the XBR CLI, provide your WAMP client private key using the command line argument ``--cskey=0x`` appended
with your key:

.. code-block:: console

    --cskey=0xecdc5e97...

You can also persistently store your WAMP client private key in the CLI configuration file for one of the user
profiles you have there:

.. code-block:: console

    $ cat ${HOME}/.xbrnetwork/config.ini
    [default]

    # user private WAMP client key
    cskey=0xecdc5e97...

.. note::

    Obviously, you must protect your *private key*! The *public key* of WAMP client key pair is not security
    sensitive. Even the public key however should always be treated carefully regarding privacy. When you
    store your private key in the CLI configuration file, make sure to protect this file using
    ``chmod 600 ${HOME}/.xbrnetwork/config.ini``.


CLI User Profile
----------------

The CLI maintains a local user configuration file in ``${HOME}/.xbrnetwork/config.ini``.
The configuration file will contain at least one (CLI) user profile.
To create a new CLI configuration file and user profile:

.. code-block:: console

    $ xbrnetwork
    created new local user directory /home/oberstet/.xbrnetwork
    creating new user profile "default"
    enter a XBR data market URL: wss://markets.international-data-monetization-award.com/ws
    enter the WAMP realm of the XBR data market: idma
    your private Etherum key: 0x4C1F7...
    your private WAMP client key: 0x7e8f...
    your Infura gateway key: 40c69...
    your Infura gateway secret: 55119...
    created new local user configuration /home/oberstet/.xbrnetwork/config.ini
    user profile "default" loaded


Not a member yet
----------------

Before you have registered in the XBR Network, this is what you get:

.. code-block:: console

    $ xbrnetwork get-member

.. thumbnail:: _static/screenshots/xbr-cli-not-a-member-yet.png

On-boarding
-----------

To on-board and register in the XBR Network using the CLI, submit a request providing your Ethereum private key, your
client key, as well as your username and email:

.. code-block:: console

    $ xbrnetwork register-member \
    --cskey=0x7e8f... \
    --ethkey=0x4C1F7... \
    --username=oberstet5 \
    --email=tobias.oberstein@gmail.com

.. note::

    Of course, neither your username nor your email is stored on-chain (on the blockchain). Your email is required so that
    we can send a verification code to you (see next step).

This is what you should see:

.. code-block:: console

    (cpy382_1) oberstet@intel-nuci7:~/scm/crossbario/autobahn-python$ xbrnetwork register-member \
    > --username=oberstet6 \
    > --email=tobias.oberstein@gmail.com
    2020-06-05T18:23:18+0200 XBR CLI v20.6.1
    2020-06-05T18:23:18+0200 Profile default loaded from /home/oberstet/.xbrnetwork/config.ini
    2020-06-05T18:23:18+0200 Connecting to "wss://planet.xbr.network/ws" at realm "xbrnetwork" ..
    2020-06-05T18:23:18+0200 Client Ethereum key loaded, public address is 0x66290fA8ADcD901Fd994e4f64Cfb53F4c359a326
    2020-06-05T18:23:18+0200 Client WAMP authentication key loaded, public key is 0x7172c38631864153e16f4db7a4a7ff0e2fbe7a180591d28d60e909d77d644964
    2020-06-05T18:23:18+0200 Client connected, now joining realm "xbrnetwork" with WAMP-cryptosign authentication ..
    2020-06-05T18:23:18+0200 Ok, client joined on realm "xbrnetwork" [session=3664895410309954, authid="anonymous-T3WJ-LLHN-AYFW-64WP-TXPM-W53F", authrole="anonymous"]
    2020-06-05T18:23:18+0200 not yet a member in the XBR network
    2020-06-05T18:23:20+0200 On-boarding member - verification "dc65d1e9-2387-4226-a1dc-d50f80531574" created
    2020-06-05T18:23:20+0200 Client left realm (reason="wamp.close.normal")
    2020-06-05T18:23:20+0200 Client disconnected
    2020-06-05T18:23:20+0200 Main loop terminated.

You should receive an email with a verification action ID such as ``072061e8-d1b4-4988-9524-6873b4d5784e`` and
a verification code such as ``5QRM-R5KR-7PGU``.

Verify the on-boarding request using the verification action and code:

.. code-block:: console

    $ xbrnetwork register-member-verify \
    --vaction=dc65d1e9-2387-4226-a1dc-d50f80531574 \
    --vcode=A346-GJLE-64SW

This is what you should see:

.. code-block:: console

    $ xbrnetwork register-member-verify \
    > --vaction=dc65d1e9-2387-4226-a1dc-d50f80531574 \
    > --vcode=A346-GJLE-64SW
    2020-06-05T18:27:08+0200 XBR CLI v20.6.1
    2020-06-05T18:27:08+0200 Profile default loaded from /home/oberstet/.xbrnetwork/config.ini
    2020-06-05T18:27:08+0200 Connecting to "wss://planet.xbr.network/ws" at realm "xbrnetwork" ..
    2020-06-05T18:27:08+0200 Client Ethereum key loaded, public address is 0x66290fA8ADcD901Fd994e4f64Cfb53F4c359a326
    2020-06-05T18:27:08+0200 Client WAMP authentication key loaded, public key is 0x7172c38631864153e16f4db7a4a7ff0e2fbe7a180591d28d60e909d77d644964
    2020-06-05T18:27:08+0200 Client connected, now joining realm "xbrnetwork" with WAMP-cryptosign authentication ..
    2020-06-05T18:27:08+0200 Ok, client joined on realm "xbrnetwork" [session=8735495987511209, authid="anonymous-N7PW-H7F7-TPCP-ATFP-9X49-GA9C", authrole="anonymous"]
    2020-06-05T18:27:08+0200 not yet a member in the XBR network
    2020-06-05T18:27:08+0200 Verifying member using vaction_oid=dc65d1e9-2387-4226-a1dc-d50f80531574, vaction_code=A346-GJLE-64SW ..
    2020-06-05T18:27:08+0200 SUCCESS! New XBR Member onboarded: member_oid=ab4dd6fd-6250-4cda-81ba-97f7d52ceac9, result=
    {'created': 1591374428420644124,
     'member_oid': b'\xabM\xd6\xfdbPL\xda\x81\xba\x97\xf7\xd5,\xea\xc9',
     'transaction': b'\xa4\xa7W\xfe"\x16\xe1l\x9f\xe0\xf7\x18\x8ak\xeb\xba'
                    b'J\xd5S\xb6\xd9\x99\x9d\x96\xce\x1c\xbcw1\xcd\xec%'}
    2020-06-05T18:27:08+0200 Client left realm (reason="wamp.close.normal")
    2020-06-05T18:27:08+0200 Client disconnected
    2020-06-05T18:27:08+0200 Main loop terminated.

To access your new XBR Network member profile, run:

.. code-block:: console

    $ xbrnetwork get-member

This is what you should see:

.. code-block:: console

    $ xbrnetwork get-member
    2020-06-05T18:28:38+0200 XBR CLI v20.6.1
    2020-06-05T18:28:38+0200 Profile default loaded from /home/oberstet/.xbrnetwork/config.ini
    2020-06-05T18:28:38+0200 Connecting to "wss://planet.xbr.network/ws" at realm "xbrnetwork" ..
    2020-06-05T18:28:38+0200 Client Ethereum key loaded, public address is 0x66290fA8ADcD901Fd994e4f64Cfb53F4c359a326
    2020-06-05T18:28:38+0200 Client WAMP authentication key loaded, public key is 0x7172c38631864153e16f4db7a4a7ff0e2fbe7a180591d28d60e909d77d644964
    2020-06-05T18:28:38+0200 Client connected, now joining realm "xbrnetwork" with WAMP-cryptosign authentication ..
    2020-06-05T18:28:38+0200 Ok, client joined on realm "xbrnetwork" [session=6918284698412513, authid="member-ab4dd6fd-6250-4cda-81ba-97f7d52ceac9", authrole="member"]
    2020-06-05T18:28:39+0200 Member found:

    {'address': '0x66290fA8ADcD901Fd994e4f64Cfb53F4c359a326',
     'balance': {'eth': Decimal('0.199585784'), 'xbr': 0},
     'catalogs': 0,
     'created': numpy.datetime64('2020-06-05T16:27:08.420644124'),
     'domains': 0,
     'email': 'tobias.oberstein@gmail.com',
     'eula': 'QmeHTWw717jPEF6aJqhNMrXx4KLrDiTHi5m7gfbjA1BqMj',
     'level': 'ACTIVE',
     'markets': 0,
     'oid': UUID('ab4dd6fd-6250-4cda-81ba-97f7d52ceac9'),
     'profile': 'QmV1eeDextSdUrRUQp9tUXF8SdvVeykaiwYLgrXHHVyULY',
     'username': 'oberstet6'}

    2020-06-05T18:28:39+0200 Client left realm (reason="wamp.close.normal")
    2020-06-05T18:28:39+0200 Client disconnected
    2020-06-05T18:28:39+0200 Main loop terminated.


XBR Token Transfer
------------------

When doing ``xbrnetwork get-member``, the information returned will include both your current on-chain ETH balance,
as well as your balance of XBR Token (which is one coin that can be used as a market-payment-coin in markets
configured to use XBR as a means of payment).

Transferring XBR tokens looks like this

.. thumbnail:: _static/screenshots/xbr-token-transfer.png

This transfer of 1000 XBR to some target address did cost 0.001541 ETH (or 0.33 EUR) on Rinkeby testnet.

After the transfer (to that member), the member information returned will look like this:

.. thumbnail:: _static/screenshots/xbr-token-transfer-after.png


Getting market information
--------------------------

To get information about an existing XBR data market:

.. code-block:: console

    $ xbrnetwork get-market \
    --market=1388ddf6-fe36-4201-b1aa-cb7e36b4cfb3


Creating a market
-----------------

To create a new XBR data market, generate a new market UUID:

.. code-block:: console

    $ /usr/bin/uuidgen
    394205e5-5d3d-4eab-a7e8-6c4de21bc76d

.. code-block:: console

    xbrnetwork create-market \
    --market 394205e5-5d3d-4eab-a7e8-6c4de21bc76d \
    --market_title "IDMA test market 1" \
    --market_label "idma-market1" \
    --market_homepage https://markets.international-data-monetization-award.com/market1 \
    --provider_security 0 \
    --consumer_security 0 \
    --market_fee 0 \
    --marketmaker 0x163D58cE482560B7826b4612f40aa2A7d53310C4

.. code-block:: console

    $ xbrnetwork create-market \
    > --market 394205e5-5d3d-4eab-a7e8-6c4de21bc76d \
    > --market_title "IDMA test market 1" \
    > --market_label "idma-market1" \
    > --market_homepage https://markets.international-data-monetization-award.com/market1 \
    > --provider_security 0 \
    > --consumer_security 0 \
    > --market_fee 0 \
    > --marketmaker 0x163D58cE482560B7826b4612f40aa2A7d53310C4
    2020-06-05T20:54:47+0200 XBR CLI v20.6.1
    2020-06-05T20:54:47+0200 Profile default loaded from /home/oberstet/.xbrnetwork/config.ini
    2020-06-05T20:54:47+0200 Connecting to "wss://planet.xbr.network/ws" at realm "xbrnetwork" ..
    2020-06-05T20:54:48+0200 Client Ethereum key loaded, public address is 0x66290fA8ADcD901Fd994e4f64Cfb53F4c359a326
    2020-06-05T20:54:48+0200 Client WAMP authentication key loaded, public key is 0x7172c38631864153e16f4db7a4a7ff0e2fbe7a180591d28d60e909d77d644964
    2020-06-05T20:54:48+0200 Client connected, now joining realm "xbrnetwork" with WAMP-cryptosign authentication ..
    2020-06-05T20:54:48+0200 Ok, client joined on realm "xbrnetwork" [session=6290962938304946, authid="member-ab4dd6fd-6250-4cda-81ba-97f7d52ceac9", authrole="member"]
    2020-06-05T20:54:49+0200 Total markets before: 3
    2020-06-05T20:54:49+0200 Market for owner: 0
    2020-06-05T20:54:55+0200 SUCCESS: Create market request submitted:
    {'action': 'create_market',
     'timestamp': 1591383295497514499,
     'vaction_oid': b'\x14\xd5\xe8\xf8\x0f\x9aM\\\x97{\xbd4\x159\xf1\xba'}

    2020-06-05T20:54:55+0200 SUCCESS: New Market verification "14d5e8f8-0f9a-4d5c-977b-bd341539f1ba" created
    2020-06-05T20:54:55+0200 Client left realm (reason="wamp.close.normal")
    2020-06-05T20:54:55+0200 Client disconnected
    2020-06-05T20:54:55+0200 Main loop terminated.




Joining a market
----------------

To join a XBR data market, you will need the XBR data market ID, such as ``1388ddf6-fe36-4201-b1aa-cb7e36b4cfb3``
(which is the IDMA test market).

Here is how to join as an actor in that market as both a buyer and seller:

.. code-block:: console

    $ xbrnetwork join-market \
    --market=1388ddf6-fe36-4201-b1aa-cb7e36b4cfb3 \
    --actor_type=3

You will receive an email with a verification action ID and a verification code. Submit these
to complete joining the market:

.. code-block:: console

    xbrnetwork join-market-verify \
    --vaction=ddcd5452-28cc-4ecb-a0f3-8fc8b596f9a5 \
    --vcode=AGGA-PK6G-57NY

To access your actor status in a market, run:

.. code-block:: console

    $ xbrnetwork get-actor \
    --market=1388ddf6-fe36-4201-b1aa-cb7e36b4cfb3


Opening a channel
-----------------

