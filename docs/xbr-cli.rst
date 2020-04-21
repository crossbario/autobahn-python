XBR Command line interface
==========================

Autobahn includes a command-line interface for the `XBR network <https://xbr.network>`__:

.. code-block:: console

    $ xbrnetwork --help

    usage: xbrnetwork [-h] [-d] [--url URL] [--realm REALM] [--ethkey ETHKEY] [--cskey CSKEY] [--username USERNAME] [--email EMAIL] [--market MARKET] [--marketmaker MARKETMAKER] [--actor_type {2,1,3}] [--vcode VCODE] [--vaction VACTION]
                    {onboard,onboard-verify,create-market,create-market-verify,join-market,join-market-verify}

    positional arguments:
    {onboard,onboard-verify,create-market,create-market-verify,join-market,join-market-verify}
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
    --marketmaker MARKETMAKER
                            For creating new markets, the market maker address.
    --actor_type {1,2,3}  Actor type: PROVIDER = 1, CONSUMER = 2, PROVIDER_CONSUMER (both) = 3
    --vcode VCODE         For verifications of actions, the verification UUID.
    --vaction VACTION     For verifications of actions (on-board, create-market, ..), the verification code.


On-board member
---------------

Submit request to on-board new member in the XBR network:

.. code-block:: console

    $ xbrnetwork --cskey=0x6cba0... --ethkey=0x7584... --username=oberstet1 --email=tobias.oberstein@gmail.com onboard

    2020-04-21T12:00:33+0200 Client.__init__(config=ComponentConfig(realm=<xbrnetwork>, extra={'command': 'onboard', 'ethkey': b'u\x84\x8d\xdb\x11U\xcd\x1c\xdfmt\xa6\xe7\xfb\xed\x06\xae\xaa!\xef-\x8a\x05\xdfz\xf2\xd9\\\xdc\x12vr', 'cskey': b'l\xba\x0f\x9c\xec\x8b<G\xbd\x04T\x15\x16\xa9y\xe6?\x13\x1f\xa9;\xf4P\xe2N\x1f\x15\x85h\xbc\xfa\x1a', 'username': 'oberstet1', 'email': 'tobias.oberstein@gmail.com', 'vcode': None, 'vaction': None}, keyring=None, controller=None, shared=None, runner=<autobahn.twisted.wamp.ApplicationRunner object at 0x7f8ea56ec040>))
    2020-04-21T12:00:33+0200 Client (delegate) Ethereum key loaded (adr=0x0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047)
    2020-04-21T12:00:33+0200 Client (delegate) WAMP-cryptosign authentication key loaded (pubkey=0xe545a23b971a624d735f75ecf88676aa5170c14c4bc03bf31e88faaa7b28187f)
    2020-04-21T12:00:33+0200 Client.onConnect()
    2020-04-21T12:00:33+0200 Client.onChallenge(challenge=Challenge(method=cryptosign, extra={'challenge': '19c446edc6c87924814790fea75a0487ced6b7a6736d763e3b9f5d5ff4fdd078', 'channel_binding': 'tls-unique'}))
    2020-04-21T12:00:33+0200 Client.onJoin(details=
    SessionDetails(realm="xbrnetwork",
                session=7150418774024691,
                authid="anonymous-QMM6-N4QH-4NSM-Y3NL-FKHH-HK6N",
                authrole="anonymous",
                authmethod="cryptosign",
                authprovider="dynamic",
                authextra={'x_cb_node': '5f1fcfbd-64d6-4929-949d-ad6cada0ea0b', 'x_cb_worker': 'rtr1', 'x_cb_peer': 'tcp4:213.170.219.39:8848', 'x_cb_pid': 2027},
                serializer="cbor",
                transport="websocket",
                resumed=None,
                resumable=None,
                resume_token=None))
    2020-04-21T12:00:33+0200 not yet a member in the XBR network
    2020-04-21T12:00:39+0200 On-boarding member - verification "276450ce-cf17-4053-a83e-1a9ec053b4f8" created
    2020-04-21T12:00:39+0200 Client.onLeave(details=CloseDetails(reason=<wamp.close.normal>, message='None'))
    2020-04-21T12:00:39+0200 Shutting down ..
    2020-04-21T12:00:39+0200 Client.onDisconnect()
    2020-04-21T12:00:39+0200 Main loop terminated.

Verify the on-boarding request:

.. code-block:: console

    $ xbrnetwork --cskey=0x6cba0... --ethkey=0x7584... --vaction=276450ce-cf17-4053-a83e-1a9ec053b4f8 --vcode=TFMC-KPRR-NNVE onboard-verify

    2020-04-21T12:02:24+0200 Client.__init__(config=ComponentConfig(realm=<xbrnetwork>, extra={'command': 'onboard-verify', 'ethkey': b'u\x84\x8d\xdb\x11U\xcd\x1c\xdfmt\xa6\xe7\xfb\xed\x06\xae\xaa!\xef-\x8a\x05\xdfz\xf2\xd9\\\xdc\x12vr', 'cskey': b'l\xba\x0f\x9c\xec\x8b<G\xbd\x04T\x15\x16\xa9y\xe6?\x13\x1f\xa9;\xf4P\xe2N\x1f\x15\x85h\xbc\xfa\x1a', 'username': None, 'email': None, 'vcode': 'TFMC-KPRR-NNVE', 'vaction': UUID('276450ce-cf17-4053-a83e-1a9ec053b4f8')}, keyring=None, controller=None, shared=None, runner=<autobahn.twisted.wamp.ApplicationRunner object at 0x7f9b544e81f0>))
    2020-04-21T12:02:24+0200 Client (delegate) Ethereum key loaded (adr=0x0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047)
    2020-04-21T12:02:24+0200 Client (delegate) WAMP-cryptosign authentication key loaded (pubkey=0xe545a23b971a624d735f75ecf88676aa5170c14c4bc03bf31e88faaa7b28187f)
    2020-04-21T12:02:24+0200 Client.onConnect()
    2020-04-21T12:02:25+0200 Client.onChallenge(challenge=Challenge(method=cryptosign, extra={'challenge': 'ee7b0c616532c0000748cf699d63ec8579bdb20a793f3d8a08dc3711deaff563', 'channel_binding': 'tls-unique'}))
    2020-04-21T12:02:25+0200 Client.onJoin(details=
    SessionDetails(realm="xbrnetwork",
                session=1192999217896284,
                authid="anonymous-6HTR-KUTW-VKAL-AWVU-H6S6-HWH3",
                authrole="anonymous",
                authmethod="cryptosign",
                authprovider="dynamic",
                authextra={'x_cb_node': '5f1fcfbd-64d6-4929-949d-ad6cada0ea0b', 'x_cb_worker': 'rtr1', 'x_cb_peer': 'tcp4:213.170.219.39:8858', 'x_cb_pid': 2027},
                serializer="cbor",
                transport="websocket",
                resumed=None,
                resumable=None,
                resume_token=None))
    2020-04-21T12:02:25+0200 not yet a member in the XBR network
    2020-04-21T12:02:25+0200 Verifying member using vaction_oid=276450ce-cf17-4053-a83e-1a9ec053b4f8, vaction_code=TFMC-KPRR-NNVE ..
    2020-04-21T12:02:25+0200 SUCCESS! New XBR Member onboarded: member_oid=d08e6a3a-4748-4228-8737-d1e38d2dbfd8, result=
    {'created': 1587463345067963095,
    'member_oid': b'\xd0\x8ej:GHB(\x877\xd1\xe3\x8d-\xbf\xd8',
    'transaction': b'\xfc#\xf6\x98\x9f}V!\x93\xf9\xdcq\x10\x9e\x91\x00'
                    b'\x8a\xd2\xf4\xe6+K\x7f\xed\x81.M\x1e\x1cb&9'}
    2020-04-21T12:02:25+0200 Client.onLeave(details=CloseDetails(reason=<wamp.close.normal>, message='None'))
    2020-04-21T12:02:25+0200 Shutting down ..
    2020-04-21T12:02:25+0200 Client.onDisconnect()
    2020-04-21T12:02:25+0200 Main loop terminated.


Get member
----------

To get member information (about oneself):

.. code-block:: console

    $ xbrnetwork --cskey=0xfbb... --ethkey=0x5be59... get-member

    2020-04-21T14:51:26+0200 Client.__init__(config=ComponentConfig(realm=<xbrnetwork>, extra={'command': 'get-member', 'ethkey': b'[\xe5\x99\xa3I\'\xa1\x11\t"\xd7pK\xa3\x16\x14K1i\x9d\x8e\x7f"\x9e&\x84\xd5WZ\x84!N', 'cskey': b"\xfb\xb1\xd2\x08\x0c.\x1d\xaa\x8e)'+~\xc7\xe7K.#=\x1b\xda\xa4\xa3h>\xa7\x9d#<\xd6u\x89", 'username': None, 'email': None, 'market': None, 'marketmaker': None, 'actor_type': None, 'vcode': None, 'vaction': None}, keyring=None, controller=None, shared=None, runner=<autobahn.twisted.wamp.ApplicationRunner object at 0x7f3bae0ebb20>))
    2020-04-21T14:51:26+0200 Client (delegate) Ethereum key loaded (adr=0x0x2F070c2f49a59159A0346396f1139203355ACA43)
    2020-04-21T14:51:26+0200 Client (delegate) WAMP-cryptosign authentication key loaded (pubkey=0x7e8956c3242a687470992175f950857679956e2ff49bf994bfeece491fd8a21d)
    2020-04-21T14:51:26+0200 Client.onConnect()
    2020-04-21T14:51:27+0200 Client.onChallenge(challenge=Challenge(method=cryptosign, extra={'challenge': '19fc396940262ec3bb12f5836bee0e71a0ba96e388ff107567b4c58ff87396b4', 'channel_binding': 'tls-unique'}))
    2020-04-21T14:51:27+0200 Client.onJoin(details=
    SessionDetails(realm="xbrnetwork",
                session=1273988983194228,
                authid="member-eddcf37f-79cd-464f-b629-bf3c71f0ecce",
                authrole="member",
                authmethod="cryptosign",
                authprovider="dynamic",
                authextra={'x_cb_node': '5f1fcfbd-64d6-4929-949d-ad6cada0ea0b', 'x_cb_worker': 'rtr1', 'x_cb_peer': 'tcp4:213.170.219.39:10272', 'x_cb_pid': 2027},
                serializer="cbor",
                transport="websocket",
                resumed=None,
                resumable=None,
                resume_token=None))
    2020-04-21T14:51:27+0200 already a member in the XBR network:

    {'address': b'/\x07\x0c/I\xa5\x91Y\xa04c\x96\xf1\x13\x92\x035Z\xcaC',
    'balance': {'eth': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x02\xc5K\xba\x10u\xa2\x00',
                'xbr': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00'},
    'catalogs': 0,
    'created': 1587469642821232764,
    'domains': 0,
    'email': 'tobias.oberstein@gmail.com',
    'eula': 'QmRRvwEyT7oAM4rhGZFZXWQWNz1rEyiahgNuYy1Lxo4P6Z',
    'level': 1,
    'markets': 0,
    'oid': b'\xed\xdc\xf3\x7fy\xcdFO\xb6)\xbf<q\xf0\xec\xce',
    'profile': 'QmV1eeDextSdUrRUQp9tUXF8SdvVeykaiwYLgrXHHVyULY',
    'username': 'oberstet2'}

    2020-04-21T14:51:28+0200 Found member with address 0x2F070c2f49a59159A0346396f1139203355ACA43, member level 1: 0 ETH, 0 XBR
    2020-04-21T14:51:28+0200 Client.onLeave(details=CloseDetails(reason=<wamp.close.normal>, message='None'))
    2020-04-21T14:51:28+0200 Shutting down ..
    2020-04-21T14:51:28+0200 Client.onDisconnect()
    2020-04-21T14:51:28+0200 Main loop terminated.


Create market
-------------

Submit request to create a new data market in the network:

.. code-block:: console

    $ xbrnetwork --cskey=0x6cba0... --ethkey=0x7584... --market=1388ddf6-fe36-4201-b1aa-cb7e36b4cfb3 --marketmaker=0x31C2891b219575F119ad4a9083C089153382F0A5 create-market

    2020-04-21T12:54:38+0200 Client.__init__(config=ComponentConfig(realm=<xbrnetwork>, extra={'command': 'create-market', 'ethkey': b'u\x84\x8d\xdb\x11U\xcd\x1c\xdfmt\xa6\xe7\xfb\xed\x06\xae\xaa!\xef-\x8a\x05\xdfz\xf2\xd9\\\xdc\x12vr', 'cskey': b'l\xba\x0f\x9c\xec\x8b<G\xbd\x04T\x15\x16\xa9y\xe6?\x13\x1f\xa9;\xf4P\xe2N\x1f\x15\x85h\xbc\xfa\x1a', 'username': None, 'email': None, 'market': UUID('1388ddf6-fe36-4201-b1aa-cb7e36b4cfb3'), 'marketmaker': b'1\xc2\x89\x1b!\x95u\xf1\x19\xadJ\x90\x83\xc0\x89\x153\x82\xf0\xa5', 'vcode': None, 'vaction': None}, keyring=None, controller=None, shared=None, runner=<autobahn.twisted.wamp.ApplicationRunner object at 0x7f26aba8d400>))
    2020-04-21T12:54:39+0200 Client (delegate) Ethereum key loaded (adr=0x0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047)
    2020-04-21T12:54:39+0200 Client (delegate) WAMP-cryptosign authentication key loaded (pubkey=0xe545a23b971a624d735f75ecf88676aa5170c14c4bc03bf31e88faaa7b28187f)
    2020-04-21T12:54:39+0200 Client.onConnect()
    2020-04-21T12:54:39+0200 Client.onChallenge(challenge=Challenge(method=cryptosign, extra={'challenge': '71d59158fd8720fd7da41c5587c7652838bb5e4a1f17220e476cc303ad13bbf4', 'channel_binding': 'tls-unique'}))
    2020-04-21T12:54:39+0200 Client.onJoin(details=
    SessionDetails(realm="xbrnetwork",
                session=783576629122096,
                authid="member-d08e6a3a-4748-4228-8737-d1e38d2dbfd8",
                authrole="member",
                authmethod="cryptosign",
                authprovider="dynamic",
                authextra={'x_cb_node': '5f1fcfbd-64d6-4929-949d-ad6cada0ea0b', 'x_cb_worker': 'rtr1', 'x_cb_peer': 'tcp4:213.170.219.39:9160', 'x_cb_pid': 2027},
                serializer="cbor",
                transport="websocket",
                resumed=None,
                resumable=None,
                resume_token=None))
    2020-04-21T12:54:39+0200 already a member in the XBR network:

    {'address': b'\xec\xdb@\xc2\xb3O;\xa1b\xc4\x13\xccS\xba<\xa9\x9f\xf8\xa0G',
    'balance': {'eth': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x02\xc50q%\x1d\xc2\x00',
                'xbr': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00'},
    'catalogs': 0,
    'created': 1587463345067963095,
    'domains': 0,
    'email': 'tobias.oberstein@gmail.com',
    'eula': 'QmawsPbwU8aJPVrP4JSP5EooEhiaymxan6n6kYySWvv9wn',
    'level': 1,
    'markets': 0,
    'oid': b'\xd0\x8ej:GHB(\x877\xd1\xe3\x8d-\xbf\xd8',
    'profile': 'QmV1eeDextSdUrRUQp9tUXF8SdvVeykaiwYLgrXHHVyULY',
    'username': 'oberstet1'}

    2020-04-21T12:54:41+0200 SUCCESS: Create market request submitted:
    {'action': 'create_market',
    'timestamp': 1587466481552866698,
    'vaction_oid': b']mh\xac\xef\xa1L\xf7\x97\\y\x9a\xf5\xfdxN'}

    2020-04-21T12:54:41+0200 SUCCESS: New Market verification "5d6d68ac-efa1-4cf7-975c-799af5fd784e" created
    2020-04-21T12:54:41+0200 Client.onLeave(details=CloseDetails(reason=<wamp.close.normal>, message='None'))
    2020-04-21T12:54:41+0200 Shutting down ..
    2020-04-21T12:54:41+0200 Client.onDisconnect()
    2020-04-21T12:54:41+0200 Main loop terminated.

Verify the market creation request:

.. code-block:: console

    $ xbrnetwork --cskey=0x6cba0... --ethkey=0x7584... --vaction=5d6d68ac-efa1-4cf7-975c-799af5fd784e --vcode=VCKP-SJCP-MAJN create-market-verify

    2020-04-21T12:55:56+0200 Client.__init__(config=ComponentConfig(realm=<xbrnetwork>, extra={'command': 'create-market-verify', 'ethkey': b'u\x84\x8d\xdb\x11U\xcd\x1c\xdfmt\xa6\xe7\xfb\xed\x06\xae\xaa!\xef-\x8a\x05\xdfz\xf2\xd9\\\xdc\x12vr', 'cskey': b'l\xba\x0f\x9c\xec\x8b<G\xbd\x04T\x15\x16\xa9y\xe6?\x13\x1f\xa9;\xf4P\xe2N\x1f\x15\x85h\xbc\xfa\x1a', 'username': None, 'email': None, 'market': None, 'marketmaker': None, 'vcode': 'VCKP-SJCP-MAJN', 'vaction': UUID('5d6d68ac-efa1-4cf7-975c-799af5fd784e')}, keyring=None, controller=None, shared=None, runner=<autobahn.twisted.wamp.ApplicationRunner object at 0x7f3a6a1fd8b0>))
    2020-04-21T12:55:56+0200 Client (delegate) Ethereum key loaded (adr=0x0xecdb40C2B34f3bA162C413CC53BA3ca99ff8A047)
    2020-04-21T12:55:56+0200 Client (delegate) WAMP-cryptosign authentication key loaded (pubkey=0xe545a23b971a624d735f75ecf88676aa5170c14c4bc03bf31e88faaa7b28187f)
    2020-04-21T12:55:56+0200 Client.onConnect()
    2020-04-21T12:55:56+0200 Client.onChallenge(challenge=Challenge(method=cryptosign, extra={'challenge': '6d3dc4ae0e506caac39c019972d2b6fa6359744159953bb0abff5bf066ee6492', 'channel_binding': 'tls-unique'}))
    2020-04-21T12:55:56+0200 Client.onJoin(details=
    SessionDetails(realm="xbrnetwork",
                session=7104052105792514,
                authid="member-d08e6a3a-4748-4228-8737-d1e38d2dbfd8",
                authrole="member",
                authmethod="cryptosign",
                authprovider="dynamic",
                authextra={'x_cb_node': '5f1fcfbd-64d6-4929-949d-ad6cada0ea0b', 'x_cb_worker': 'rtr1', 'x_cb_peer': 'tcp4:213.170.219.39:9168', 'x_cb_pid': 2027},
                serializer="cbor",
                transport="websocket",
                resumed=None,
                resumable=None,
                resume_token=None))
    2020-04-21T12:55:57+0200 already a member in the XBR network:

    {'address': b'\xec\xdb@\xc2\xb3O;\xa1b\xc4\x13\xccS\xba<\xa9\x9f\xf8\xa0G',
    'balance': {'eth': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x02\xc50q%\x1d\xc2\x00',
                'xbr': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00'},
    'catalogs': 0,
    'created': 1587463345067963095,
    'domains': 0,
    'email': 'tobias.oberstein@gmail.com',
    'eula': 'QmawsPbwU8aJPVrP4JSP5EooEhiaymxan6n6kYySWvv9wn',
    'level': 1,
    'markets': 0,
    'oid': b'\xd0\x8ej:GHB(\x877\xd1\xe3\x8d-\xbf\xd8',
    'profile': 'QmV1eeDextSdUrRUQp9tUXF8SdvVeykaiwYLgrXHHVyULY',
    'username': 'oberstet1'}

    2020-04-21T12:55:57+0200 Verifying create market using vaction_oid=5d6d68ac-efa1-4cf7-975c-799af5fd784e, vaction_code=VCKP-SJCP-MAJN ..
    2020-04-21T12:55:57+0200 Create market request verified:
    {'created': 1587466557317337105,
    'market_oid': b'\x13\x88\xdd\xf6\xfe6B\x01\xb1\xaa\xcb~6\xb4\xcf\xb3',
    'transaction': b'\xb3z3\x0f\\\xc7\x11L\x9es\r\xc6\x85\xd2\x88,\x0f\x1b{\xed'
                    b'@\x89\xda\xb0\t\xdde\xdd\x8eh\xda\xaa'}

    2020-04-21T12:55:57+0200 SUCCESS! New XBR market created: market_oid=1388ddf6-fe36-4201-b1aa-cb7e36b4cfb3, result=
    {'created': 1587466557317337105,
    'market_oid': b'\x13\x88\xdd\xf6\xfe6B\x01\xb1\xaa\xcb~6\xb4\xcf\xb3',
    'transaction': b'\xb3z3\x0f\\\xc7\x11L\x9es\r\xc6\x85\xd2\x88,\x0f\x1b{\xed'
                    b'@\x89\xda\xb0\t\xdde\xdd\x8eh\xda\xaa'}
    2020-04-21T12:55:57+0200 SUCCESS - find_markets: found 2 markets
    2020-04-21T12:55:57+0200 SUCCESS - get_markets_by_owner: found 1 markets
    2020-04-21T12:55:57+0200 network.xbr.console.get_market(market_oid=b'\x13\x88\xdd\xf6\xfe6B\x01\xb1\xaa\xcb~6\xb4\xcf\xb3') ..
    2020-04-21T12:55:57+0200 SUCCESS: got market information

    {'attributes': {'homepage': 'https://markets.international-data-monetization-award.com/',
                    'label': 'IDMA',
                    'title': 'International Data Monetization Award'},
    'coin': b'\x8dA\xefd\xd4\x9e\xa1U\x0bKA\xa8\x95\x9d\x85f\x01D\x15\x03',
    'consumer_security': None,
    'created': None,
    'maker': b'1\xc2\x89\x1b!\x95u\xf1\x19\xadJ\x90\x83\xc0\x89\x153\x82\xf0\xa5',
    'market': b'\x13\x88\xdd\xf6\xfe6B\x01\xb1\xaa\xcb~6\xb4\xcf\xb3',
    'market_fee': None,
    'meta': 'QmWPFjSR61eCHnJG5GEFJf8d4QW8LW3N3PFqo6RvC15QrA',
    'owner': b'\xec\xdb@\xc2\xb3O;\xa1b\xc4\x13\xccS\xba<\xa9\x9f\xf8\xa0G',
    'provider_security': None,
    'seq': 0,
    'signature': None,
    'terms': 'QmNXqk5yEbiUYHeDboeaJY6iCGVNm4MXr5uuYqpzSeVhVh',
    'tid': None,
    'timestamp': 1587466557317337105}

    2020-04-21T12:55:57+0200 Client.onLeave(details=CloseDetails(reason=<wamp.close.normal>, message='None'))
    2020-04-21T12:55:57+0200 Shutting down ..
    2020-04-21T12:55:57+0200 Client.onDisconnect()
    2020-04-21T12:55:57+0200 Main loop terminated.


Join market
-----------

Submit new member on-boarding request:

.. code-block:: console

    $ xbrnetwork --cskey=0xfbb1d... --ethkey=0x5be5... --username=oberstet2 --email=tobias.oberstein@gmail.com onboard

    2020-04-21T13:46:13+0200 Client.__init__(config=ComponentConfig(realm=<xbrnetwork>, extra={'command': 'onboard', 'ethkey': b'[\xe5\x99\xa3I\'\xa1\x11\t"\xd7pK\xa3\x16\x14K1i\x9d\x8e\x7f"\x9e&\x84\xd5WZ\x84!N', 'cskey': b"\xfb\xb1\xd2\x08\x0c.\x1d\xaa\x8e)'+~\xc7\xe7K.#=\x1b\xda\xa4\xa3h>\xa7\x9d#<\xd6u\x89", 'username': 'oberstet2', 'email': 'tobias.oberstein@gmail.com', 'market': None, 'marketmaker': None, 'actor_type': None, 'vcode': None, 'vaction': None}, keyring=None, controller=None, shared=None, runner=<autobahn.twisted.wamp.ApplicationRunner object at 0x7fd89fc0a6d0>))
    2020-04-21T13:46:13+0200 Client (delegate) Ethereum key loaded (adr=0x0x2F070c2f49a59159A0346396f1139203355ACA43)
    2020-04-21T13:46:13+0200 Client (delegate) WAMP-cryptosign authentication key loaded (pubkey=0x7e8956c3242a687470992175f950857679956e2ff49bf994bfeece491fd8a21d)
    2020-04-21T13:46:13+0200 Client.onConnect()
    2020-04-21T13:46:13+0200 Client.onChallenge(challenge=Challenge(method=cryptosign, extra={'challenge': '55523ac840f06ba9b7d6f51e1f479d4aacbd974e9f41badc4578777f6d7227f9', 'channel_binding': 'tls-unique'}))
    2020-04-21T13:46:13+0200 Client.onJoin(details=
    SessionDetails(realm="xbrnetwork",
                session=4495107774306724,
                authid="anonymous-RY3A-4XYG-M767-U7SN-C3NM-USCF",
                authrole="anonymous",
                authmethod="cryptosign",
                authprovider="dynamic",
                authextra={'x_cb_node': '5f1fcfbd-64d6-4929-949d-ad6cada0ea0b', 'x_cb_worker': 'rtr1', 'x_cb_peer': 'tcp4:213.170.219.39:9616', 'x_cb_pid': 2027},
                serializer="cbor",
                transport="websocket",
                resumed=None,
                resumable=None,
                resume_token=None))
    2020-04-21T13:46:13+0200 not yet a member in the XBR network
    2020-04-21T13:46:15+0200 On-boarding member - verification "8657b188-6936-4053-a970-42e4d9a866ee" created
    2020-04-21T13:46:15+0200 Client.onLeave(details=CloseDetails(reason=<wamp.close.normal>, message='None'))
    2020-04-21T13:46:15+0200 Shutting down ..
    2020-04-21T13:46:15+0200 Client.onDisconnect()
    2020-04-21T13:46:15+0200 Main loop terminated.

Verify member on-boarding request:

.. code-block:: console

    $ xbrnetwork --cskey=0xfbb1d... --ethkey=0x5be5... --vcode=5QJF-MK6F-QRVQ --vaction=8657b188-6936-4053-a970-42e4d9a866ee onboard-verify

    2020-04-21T13:47:22+0200 Client.__init__(config=ComponentConfig(realm=<xbrnetwork>, extra={'command': 'onboard-verify', 'ethkey': b'[\xe5\x99\xa3I\'\xa1\x11\t"\xd7pK\xa3\x16\x14K1i\x9d\x8e\x7f"\x9e&\x84\xd5WZ\x84!N', 'cskey': b"\xfb\xb1\xd2\x08\x0c.\x1d\xaa\x8e)'+~\xc7\xe7K.#=\x1b\xda\xa4\xa3h>\xa7\x9d#<\xd6u\x89", 'username': None, 'email': None, 'market': None, 'marketmaker': None, 'actor_type': None, 'vcode': '5QJF-MK6F-QRVQ', 'vaction': UUID('8657b188-6936-4053-a970-42e4d9a866ee')}, keyring=None, controller=None, shared=None, runner=<autobahn.twisted.wamp.ApplicationRunner object at 0x7f5bb7ddcbb0>))
    2020-04-21T13:47:22+0200 Client (delegate) Ethereum key loaded (adr=0x0x2F070c2f49a59159A0346396f1139203355ACA43)
    2020-04-21T13:47:22+0200 Client (delegate) WAMP-cryptosign authentication key loaded (pubkey=0x7e8956c3242a687470992175f950857679956e2ff49bf994bfeece491fd8a21d)
    2020-04-21T13:47:22+0200 Client.onConnect()
    2020-04-21T13:47:22+0200 Client.onChallenge(challenge=Challenge(method=cryptosign, extra={'challenge': 'ef0f9b882ac8487b85d85aa4a4ac6e6bc2a50775bd59bc40caeda650c20d4ea4', 'channel_binding': 'tls-unique'}))
    2020-04-21T13:47:22+0200 Client.onJoin(details=
    SessionDetails(realm="xbrnetwork",
                session=1822866108991386,
                authid="anonymous-Q4LE-5NHV-SQJP-LNMC-XKEY-FRKT",
                authrole="anonymous",
                authmethod="cryptosign",
                authprovider="dynamic",
                authextra={'x_cb_node': '5f1fcfbd-64d6-4929-949d-ad6cada0ea0b', 'x_cb_worker': 'rtr1', 'x_cb_peer': 'tcp4:213.170.219.39:9622', 'x_cb_pid': 2027},
                serializer="cbor",
                transport="websocket",
                resumed=None,
                resumable=None,
                resume_token=None))
    2020-04-21T13:47:22+0200 not yet a member in the XBR network
    2020-04-21T13:47:22+0200 Verifying member using vaction_oid=8657b188-6936-4053-a970-42e4d9a866ee, vaction_code=5QJF-MK6F-QRVQ ..
    2020-04-21T13:47:23+0200 SUCCESS! New XBR Member onboarded: member_oid=eddcf37f-79cd-464f-b629-bf3c71f0ecce, result=
    {'created': 1587469642821232764,
    'member_oid': b'\xed\xdc\xf3\x7fy\xcdFO\xb6)\xbf<q\xf0\xec\xce',
    'transaction': b'\x90\x8e\xcc<0\xedP\xdba\x03\x9d\xeb\x1b$&j\xd9{}\r'
                    b'\x17\xff\x06\x03s<\xd9\xd9\\\x0bI\xcb'}
    2020-04-21T13:47:23+0200 Client.onLeave(details=CloseDetails(reason=<wamp.close.normal>, message='None'))
    2020-04-21T13:47:23+0200 Shutting down ..
    2020-04-21T13:47:23+0200 Client.onDisconnect()
    2020-04-21T13:47:23+0200 Main loop terminated.

Submit market join request for new member:

.. code-block:: console

    $ xbrnetwork --cskey=0xfbb1d... --ethkey=0x5be5... --market=1388ddf6-fe36-4201-b1aa-cb7e36b4cfb3 --actor_type=3 join-market

    2020-04-21T13:47:33+0200 Client.__init__(config=ComponentConfig(realm=<xbrnetwork>, extra={'command': 'join-market', 'ethkey': b'[\xe5\x99\xa3I\'\xa1\x11\t"\xd7pK\xa3\x16\x14K1i\x9d\x8e\x7f"\x9e&\x84\xd5WZ\x84!N', 'cskey': b"\xfb\xb1\xd2\x08\x0c.\x1d\xaa\x8e)'+~\xc7\xe7K.#=\x1b\xda\xa4\xa3h>\xa7\x9d#<\xd6u\x89", 'username': None, 'email': None, 'market': UUID('1388ddf6-fe36-4201-b1aa-cb7e36b4cfb3'), 'marketmaker': None, 'actor_type': 3, 'vcode': None, 'vaction': None}, keyring=None, controller=None, shared=None, runner=<autobahn.twisted.wamp.ApplicationRunner object at 0x7fd4d2cb38e0>))
    2020-04-21T13:47:33+0200 Client (delegate) Ethereum key loaded (adr=0x0x2F070c2f49a59159A0346396f1139203355ACA43)
    2020-04-21T13:47:33+0200 Client (delegate) WAMP-cryptosign authentication key loaded (pubkey=0x7e8956c3242a687470992175f950857679956e2ff49bf994bfeece491fd8a21d)
    2020-04-21T13:47:33+0200 Client.onConnect()
    2020-04-21T13:47:33+0200 Client.onChallenge(challenge=Challenge(method=cryptosign, extra={'challenge': '8a7af41f88a793623f875b6111cc0001c4ef86d32f38885767dffab8d7fac698', 'channel_binding': 'tls-unique'}))
    2020-04-21T13:47:33+0200 Client.onJoin(details=
    SessionDetails(realm="xbrnetwork",
                session=2766315047838727,
                authid="member-eddcf37f-79cd-464f-b629-bf3c71f0ecce",
                authrole="member",
                authmethod="cryptosign",
                authprovider="dynamic",
                authextra={'x_cb_node': '5f1fcfbd-64d6-4929-949d-ad6cada0ea0b', 'x_cb_worker': 'rtr1', 'x_cb_peer': 'tcp4:213.170.219.39:9626', 'x_cb_pid': 2027},
                serializer="cbor",
                transport="websocket",
                resumed=None,
                resumable=None,
                resume_token=None))
    2020-04-21T13:47:33+0200 already a member in the XBR network:

    {'address': b'/\x07\x0c/I\xa5\x91Y\xa04c\x96\xf1\x13\x92\x035Z\xcaC',
    'balance': {'eth': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x02\xc5K\xba\x10u\xa2\x00',
                'xbr': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00'},
    'catalogs': 0,
    'created': 1587469642821232764,
    'domains': 0,
    'email': 'tobias.oberstein@gmail.com',
    'eula': 'QmRRvwEyT7oAM4rhGZFZXWQWNz1rEyiahgNuYy1Lxo4P6Z',
    'level': 1,
    'markets': 0,
    'oid': b'\xed\xdc\xf3\x7fy\xcdFO\xb6)\xbf<q\xf0\xec\xce',
    'profile': 'QmV1eeDextSdUrRUQp9tUXF8SdvVeykaiwYLgrXHHVyULY',
    'username': 'oberstet2'}

    2020-04-21T13:47:35+0200 SUCCESS! XBR market join request submitted: vaction_oid=44630f46-0ded-4eaf-90aa-9fbd2925788d
    2020-04-21T13:47:35+0200 Client.onLeave(details=CloseDetails(reason=<wamp.close.normal>, message='None'))
    2020-04-21T13:47:35+0200 Shutting down ..
    2020-04-21T13:47:35+0200 Client.onDisconnect()
    2020-04-21T13:47:35+0200 Main loop terminated.

Verify market join request for member:

.. code-block:: console

    $ xbrnetwork --cskey=0xfbb1d... --ethkey=0x5be5... --vaction=44630f46-0ded-4eaf-90aa-9fbd2925788d --vcode=G3XA-PEX9-F4JV join-market-verify

    2020-04-21T13:48:39+0200 Client.__init__(config=ComponentConfig(realm=<xbrnetwork>, extra={'command': 'join-market-verify', 'ethkey': b'[\xe5\x99\xa3I\'\xa1\x11\t"\xd7pK\xa3\x16\x14K1i\x9d\x8e\x7f"\x9e&\x84\xd5WZ\x84!N', 'cskey': b"\xfb\xb1\xd2\x08\x0c.\x1d\xaa\x8e)'+~\xc7\xe7K.#=\x1b\xda\xa4\xa3h>\xa7\x9d#<\xd6u\x89", 'username': None, 'email': None, 'market': None, 'marketmaker': None, 'actor_type': None, 'vcode': 'G3XA-PEX9-F4JV', 'vaction': UUID('44630f46-0ded-4eaf-90aa-9fbd2925788d')}, keyring=None, controller=None, shared=None, runner=<autobahn.twisted.wamp.ApplicationRunner object at 0x7f6ce97b56a0>))
    2020-04-21T13:48:39+0200 Client (delegate) Ethereum key loaded (adr=0x0x2F070c2f49a59159A0346396f1139203355ACA43)
    2020-04-21T13:48:39+0200 Client (delegate) WAMP-cryptosign authentication key loaded (pubkey=0x7e8956c3242a687470992175f950857679956e2ff49bf994bfeece491fd8a21d)
    2020-04-21T13:48:39+0200 Client.onConnect()
    2020-04-21T13:48:39+0200 Client.onChallenge(challenge=Challenge(method=cryptosign, extra={'challenge': '3170ea11ac8c490754efd3ecaabf6cfc49a34e0b987bccc9a1c4a29eb3fd659d', 'channel_binding': 'tls-unique'}))
    2020-04-21T13:48:39+0200 Client.onJoin(details=
    SessionDetails(realm="xbrnetwork",
                session=5153498254436248,
                authid="member-eddcf37f-79cd-464f-b629-bf3c71f0ecce",
                authrole="member",
                authmethod="cryptosign",
                authprovider="dynamic",
                authextra={'x_cb_node': '5f1fcfbd-64d6-4929-949d-ad6cada0ea0b', 'x_cb_worker': 'rtr1', 'x_cb_peer': 'tcp4:213.170.219.39:9640', 'x_cb_pid': 2027},
                serializer="cbor",
                transport="websocket",
                resumed=None,
                resumable=None,
                resume_token=None))
    2020-04-21T13:48:39+0200 already a member in the XBR network:

    {'address': b'/\x07\x0c/I\xa5\x91Y\xa04c\x96\xf1\x13\x92\x035Z\xcaC',
    'balance': {'eth': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x02\xc5K\xba\x10u\xa2\x00',
                'xbr': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00'},
    'catalogs': 0,
    'created': 1587469642821232764,
    'domains': 0,
    'email': 'tobias.oberstein@gmail.com',
    'eula': 'QmRRvwEyT7oAM4rhGZFZXWQWNz1rEyiahgNuYy1Lxo4P6Z',
    'level': 1,
    'markets': 0,
    'oid': b'\xed\xdc\xf3\x7fy\xcdFO\xb6)\xbf<q\xf0\xec\xce',
    'profile': 'QmV1eeDextSdUrRUQp9tUXF8SdvVeykaiwYLgrXHHVyULY',
    'username': 'oberstet2'}

    2020-04-21T13:48:39+0200 SUCCESS! XBR market joined: member_oid=eddcf37f-79cd-464f-b629-bf3c71f0ecce, market_oid=b'\x13\x88\xdd\xf6\xfe6B\x01\xb1\xaa\xcb~6\xb4\xcf\xb3', actor_type=3
    2020-04-21T13:48:39+0200 Client.onLeave(details=CloseDetails(reason=<wamp.close.normal>, message='None'))
    2020-04-21T13:48:39+0200 Shutting down ..
    2020-04-21T13:48:39+0200 Client.onDisconnect()
    2020-04-21T13:48:39+0200 Main loop terminated.
