:tocdepth: 1

.. _changelog:

Changelog
=========

24.4.1
------

- new: bump minimum required Twisted version to 24.3.0 (`see also <https://github.com/crossbario/autobahn-python/pull/1634>`_)
- fix: full conformance to WAMP spec rgd allowed ranges of WAMP (session scope) IDs (`PR #1637 <https://github.com/crossbario/autobahn-python/pull/1637>`_)

23.6.2
------

- fix: use regular PyPI bitarray>=2.7.5 rather than from GitHub master

23.6.1
------

- fix: updated bitarray to make eth-account work on pypy
- fix: updated web3 and eth-abi to not use beta versions (#1616)

23.1.2
------

- fix: monkey patch web3/eth_abi for python 3.11

23.1.1
------

- fix: support for Python up to v3.11
- fix: update GitHub CI
- fix: copyright transferred to typedef int GmbH - no license change!
- fix: remove coverage crap

22.12.1
-------

* new: expand WAMP Flatbuffers schemata (session ID in each message for MUXing)
* new: update flatc v22.12.06 and regenerate WAMP Flatbuffers type libraries
* fix: Twisted 22.10.0 incompability (#1604)
* fix: Rapid Cancelling Of Tasks Can Cause InvalidStateError (#1600)
* fix: identify_realm_name_category (#1590)
* fix: support Python 3.11 (#1599)
* fix: building _nvx_utf8validator extension on non-x86 systems (#1596)
* fix: asyncio rawsocket protocol transport details (#1592)
* new: expand EIP712AuthorityCertificate; more tests

22.7.1
------

* fix: Fix a few typos in docs (#1587)
* fix: remove log noise from autobahn.websocket.protocol (#1588)
* new: add more helpers to EthereumKey and CryptosignKey (#1583)
* new: EIP712 certificate chains, incl. use for WAMP-Cryptosign
* fix: improve message logging at trace log level
* fix: forward correct TLS channel ID once the TLS handshake is complete
* new: add eip712 types for WAMP-Cryptosign certificates
* new: add more helpers to EthereumKey and CryptosignKey
* new: add EthereumKey.from_keyfile, CryptosignKey.from_keyfile, CryptosignKey.from_pubkey

22.6.1
------

* new: add SecurityModuleMemory.from_config and SecurityModuleMemory.from_keyfile
* new: moved UserKey from crossbar to autobahn
* fix: more WAMP-Cryptosign unit tests
* new: experimental WAMP API catalog support
* new: regenerate FlatBuffers WAMP messages
* fix: allow tests to pass without XBR dependencies (#1580)
* new: Flatbuffers IDL based WAMP payload validation (#1576)
* fix: restore autobahn.twisted.testing to distribution (#1578)

22.5.1
------

* new: WAMP Flatbuffers IDL and schema processing (experimental)
* new: WAMP-cryptosign trustroot (experimental)
* new: add wrapper type for CryptosignAuthextra
* fix: stricted type checking of Challenge; fix cryposign unit test;
* new: more test coverage
* fix: reduce log noise
* fix: forward channel_binding selected in Component client
* new: expand ISigningKey to provide security_module/key_id (if used)
* fix: Component cryptosign test
* fix: add type hints; fix channel_binding
* new: work on federated realms and secmods
* new: rename to and work on a.w.CryptosignKey
* new: add bip44 for cryptosign test
* fix: remove all txaio.make_logger refs from generic code (#1564)
* new: initial support for federated WAMP realms via a.x.FederatedRealm/Seeder
* new: moved utility functions and unit tests for WAMP realm name checking from Crossbar.io
* new: allow list of URLs for transports in a.t.component.Component
* new: add websocket_options to a.t.wamp.ApplicationRunner
* new: add stop_at_close flag in a.t.component.run
* fix: reduce log noise (regression) on ApplicationRunner Twisted (#1561)
* new: allow ``max_retry_delay==0`` for always-immediate auto-reconnect in ApplicationRunner on Twisted
* new: add ``websocket_options`` to WAMP ApplicationRunner on Twisted (#888)
* new: more type hints and docs

22.4.2
------

* fix: can not import autobahn.twisted.util with no-TLS (#1559)

22.4.1
------

* new: modernize SessionDetails
* new: improve ISession/ITransportHandler and implementations (#1557)
* new: expand and refactor TransportDetails (#1551)
* fix: misc fixes, add type hints, more docs (#1547)
* new: key modules for use with WAMP-cryptosign (#1544)
* fix: string formatting with binary values in TransportDetails.secure_channel_id (#1483)
* fix: never default set authid/authrole in component authenticators
* fix: TransportDetails string formatting (fixes #1486)
* fix: reading private ssh key for cryptosign (fixes #932)
* fix: do not throw (but log) when leaving a session not joined (#1542)
* fix: store WAMP authextra received (#1541)

22.3.2
------

* fix: split out UI deps into separate dist flavor (#1532)
* fix: deps for RTD builds (#1540)
* fix: use and bundle dev deps from requirements file

22.3.1
------

* fix: reduce twisted log noise for wamp clients (#1537)
* fix: roundrobin in WAMP component (#1533)
* fix: generate_token (#1531)
* fix: add GitHub URL for PyPi (#1528)

22.2.2
------

* fix: auto ping/pong logs should be debug instead of info (#1524)

22.2.1
------

* new: add auto-ping/pong configuration knob ``autoPingRestartOnAnyTraffic`` (see discussion `here <https://github.com/crossbario/autobahn-python/issues/1327>`_).
* new: extended websocket auto-ping/pong ("heartbeating") with builtin RTT measurement
* new: experimental support for ``transaction_hash`` in WAMP Publish/Call (see discussion `here <https://github.com/wamp-proto/wamp-proto/issues/391#issuecomment-998577967>`_).
* new: support decimal numbers WAMP serialization and round-tripping in both JSON and CBOR
* fix: only depend on cbor2 (for WAMP CBOR serialization), not also cbor
* fix: PyInstaller and Docker build / CI issues

22.1.1
------

* new: support Python 3.10
* new: allow optional keys in endpoint config validation
* fix: reset transport retry status when connection succeeds
* fix: update Docker/PyPy to pypy:3.8-slim

21.11.1
-------

* fix: autobahn installation in docker (#1503)
* new: refactor SigningKey class for reusability (#1500, #1501)
* new: expand XBR node pairing helpers
* fix: build with nvx by default and don't publish universal wheel. (#1493)
* fix: update wamp flatbuffer schema for r2r links
* fix: don't clobber factory (#1480)
* fix: explicitly require setuptools
* new: expand wamp auth scram and xbr argon2/hkdf (#1479)
* fix: WebSocket compression, window size (zlib wbits) == 8 is illegal nowerdays (#1477)
* fix: XBR IDL code generator - all 4 WAMP actions working now
* new: add automated build of xbrnetwork CLI (single-file EXE) in CI

21.3.1
------

* fix: Twisted v21.2.0 breaks Crossbar.io (see https://github.com/crossbario/crossbar/issues/1864)

21.2.2
------

* new: use_binary_hex_encoding option for JSON object serializer
* fix: correct some sphinx doc references
* new: minimum supported Python (language) version is now 3.7 (on CPython and PyPy)
* new: more XBR proxy/stub code generation capabilities (RPC call/invoation handlers)
* fix: wamp-cryptosign loading of keys from SSH agent
* fix: update Docker image building and build Docker multi-arch images
* new: add more WAMP-cryptosign signature test vectors and unit tests
* fix: include XBR code rendering templates in package manifest

21.2.1
------

* new: XBR ABI files now via separate package ("xbr") - substantially reduce package size for non-XBR users
* fix: circular dependency in "xbr" install flavor (prohibited pip install from github master)
* fix: XBR package manifest and CLI user profile loading

21.1.1
------

* fix: consider 'wamp.close.goodbye_and_out' a clean exit (#1450)
* fix: HASH import as well as improve diagnostics if things go wrong (#1451)
* fix: add missing jinja2 dependency for XBR CLI (#1447)
* fix: ``wamp.close.goodbye_and_out`` counts as a clean exit (#1370)

20.12.3
-------

* fix: URL must be re-encoded when doing redirect (#1439)
* fix: update and migrate CI/CD pipeline to GitHub Actions
* new: minimum supported Python (language) version is now 3.6 (on CPython and PyPy)

20.12.2
-------

* fix: derive_bip32childkey traceback (#1436)
* fix: update and adjust docker files to upstream changes

20.12.1
-------

* new: CLI commands for WAMP IDL (`xbrnetwork describe-schema / codegen-schema`)
* new: add eth address helpers (#1413)
* new: cryptosign authextra allow arbitrary keys (#1411)
* fix: adapt to planet api prefix change (#1408)
* fix: Type check improve (#1405)

20.7.1
------

* new: add market login eip. expose helpers (#1402)

20.6.2
------

* fix: xbr fixes (#1396)
* fix: use cpy 3.8 for running flake in CI
* new: Ticket1392 internal attrs (#1394)
* new: internal-only router attributes and hook for router to add custom information

20.6.1
------

* new: massive expansion of XBR CLI and EIP712 helpers
* new: more (exhaustive) serializer cross-tripping tests
* fix: some code quality and bug-risk issues (#1379)
* fix: removed externalPort assignment when not set (#1378)
* fix: docs link in README (#1381)
* fix: docs typo frameword -> framework (#1380)
* fix: improve logging; track results on observable mixin
* new: add environmental variable that strips xbr. (#1374)
* fix: trollius is gone (#1373)
* new: added ability to disable TLS channel binding (#1368)

20.4.3
------

* new: XBR CLI (#1367)
* fix: add missing XBR dependency `py-multihash`

20.4.2
------

* new: XBR - package XBR v20.4.2 ABI files
* new: XBR - adjust eip712 signature for channel close
* new: XBR - adjustments after xbr refactoring (#1357)
* new: XBR - add channel open/close eip712 types to AB (#1358)
* new: WAMP-cryptosign - make channel_id_type optional in transport_channel_id()

20.4.1
------

* new: XBR ABI files are downloaded from upstream and extracted into package (fixes #1349)
* new: expose new XBR top-level contracts
* fix: bump dependencies versions for attrs and identity (#1346)
* fix: FrontendProxyProtocol object has no attribute 'write' (#1339)
* fix: WAMP-cryptosign authid is not mandatory; reduce log noise (#1340)

20.3.1
------

* fix: confusion between paying and payment channel (#1337)
* new: forward explicitly set app level errors from ApplicationRunner.run() (#1336)
* fix: simple typo: hookinh -> hooking (#1333)
* new: update for xbr v20.3.1
* fix: for #1327 - cancel Auto Ping Timeout  (#1328)
* new: helper function to create a configured Web3 blockchain connection (#1329)

20.2.2
------

* new: update XBR ABI files to XBR release v20.2.2

20.2.1
------

* new: update XBR ABI files to XBR release v20.2.1
* fix: add AuthAnonymous to __all__ (#1303)

20.1.3
------

* fix: CI building (caching?) issue "corrupt ZIP file"
* fix: update docker image build scripts and add ARM64/PyPy
* fix: update XBR ABI files
* fix: use txaio.time_ns and drop deprecated autobahn.util.time_ns
* fix: update project README and docs for supported python versions (#1296)
* fix: WebSocket protocol instances now raise `autobahn.exception.Disconnected` when sending on a closed connection (#1002)
* fix: version conflict in xbr downstream application dependency (crossbarfx) (#1295)

20.1.2
------

* fix: add `python_requires>=3.5` to prevent installation on python 2 (#1293)

20.1.1
------

* IMPORTANT: beginning release v20.1.1, Autobahn|Python only supports Python 3.5 or later.
* fix: first part of cleaning up code, dropping Python 2 support (#1282).

19.11.2
-------

* IMPORTANT: release v19.11.2 will be the last release supporting Python 2. We will support Python 3.5 and later beginning with Autobahn v20.1.1.
* fix: add docs for parameters to component.py (#1276)
* new: statistics tracking on WAMP serializers :class:`autobahn.wamp.serializer.Serializer`
* new: helper autobahn.util.time_ns

19.11.1
-------

* fix: argument type check for fragmentSize in sendMessage
* new: start_loop option for WAMP components
* new: ethereum bip39/32 helpers
* new: enable XBR in Docker image build scripts

19.10.1
-------

* new: updated docker image scripts
* new: add WAMP serializer in use to SessionDetails
* fix: partial support for xb buyers/sellers in pypy
* fix: remove dependency on "ethereum" package (part of pypy support)

19.9.3
------

* new: XBR - update XBR for new contract ABIs
* new: XBR - payment channel close
* new: XBR - implement EIP712 signing of messages in endpoints

19.9.2
------

* new: XBR - update XBR for new contract ABIs

19.9.1
------

* new: XBR - update XBR for new contract ABIs

19.8.1
------

* new: implement XBR off-chain delegate transaction signing and verification (#1202)
* new: update XBR for new contract ABIs

19.7.2
------

* fix: monkey patch re-add removed helper functions removed in eth-abi
* new: simple blockchain (XBR) client
* new: update XBR ABI files
* new: XBR endpoint transaction signing
* new: client side catching of WAMP URI errors in `session.call|register|publish|subscribe`

19.7.1
------

* fix: implement client side payload exceed max size; improve max size exceeded handling
* fix: detect when our transport is "already" closed at connect time (#1215)
* fix: XBR examples

19.6.2
------

* fix: add forgotten cryptography dependency (#1205)

19.6.1
------

* new: XBR client library integrated (#1201)
* new: add entropy depletion unit tests
* fix: make CLI tool python2 compatible (#1197)
* fix: use cryptography pbkdf2 instead of custom (#1198)
* fix: include tests for packaging (#1194)

19.5.1
------

* fix: authextra merging (#1191)
* fix: set default retry_delay_jitter (#1190)
* new: add rawsocket + twisted example (#1189)
* new: WebSocket testing support, via Agent-style interface (#1186)
* new: decorator for on_connectfailure
* fix: delayed call leakage (#1152)
* new: CLI client (#1150)
* fix: set up TLS over proxy properly (#1149)
* new: expose ser modules (#1148)
* fix: base64 encodings, add hex encoding (#1146)
* new: onConnecting callback (with TransportDetails and
  ConnectingRequest). **Note**: if you've implemented a pure
  `IWebSocketChannel` without inheriting from Autobahn base classes,
  you'll need to add an `onConnecting()` method that just does `return
  None`.

19.3.3
------

* fix: RegisterOptions should have details|bool parameter (#1143)
* new: WAMP callee disclosure
* new: WAMP forward_for in more message types; expose forward_for in options/details types
* new: expose underlying serializer modules on WAMP object serializers
* fix: WAMP-cryptosign fix base64 encodings, add hex encoding (#1146)

19.3.2
------

* fix: import guards for flatbuffers (missed in CI as we run with "all deps installed" there)

19.3.1
------

* new: add experimental support for WAMP-FlatBuffers serializer: EVENT and PUBLISH messages for now only
* new: add FlatBuffers schema for WAMP messages
* fix: improve serializer package preference behavior depending on CPy vs PyPy
* fix: relax protocol violations: ignore unknown INTERRUPT and GOODBYE already sent; reduce log noise
* fix: skipping Yield message if transport gets closed before success callback is called (#1119)
* fix: integer division in logging in py3 (#1120)
* fix: Await tasks after they've been cancelled in `autobahn.asycio.component.nicely_exit` (#1116)

19.2.1
------

* fix: set announced roles on appsession object (#1109)
* new: lower log noise on ApplicationErrors (#1107)
* new: allow explicit passing of tx endpoint and reactor (#1103)
* new: add attribute to forward applicationrunner to applicationsession via componentconfig

19.1.1
------

* new: adding marshal on SessionDetails

18.12.1
-------

* fix: return the wrapped function from component decorators (#1093)
* new: add proxy= support for Component transports (#1091)
* fix: Ticket1077 stop start (#1090)
* fix: cleanup cancel handling (#1087)

18.11.2
-------

* fix: asyncio unregisterProducer raises exception (#1079)
* fix: URL is not required in RawSocket configuration items with WAMP component API
* fix: revert PR https://github.com/crossbario/autobahn-python/pull/1075

18.11.1
-------

* new: forward_for WAMP message attribute (for Crossbar.io Router-to-Router federation)
* new: support RawSocket URLs (eg "rs://localhost:5000" or "rs://unix:/tmp/file.sock")
* new: support WAMP-over-Unix sockets for WAMP components ("new API")
* fix: use same WAMP serializer construction code for WAMP components ("new API") and ApplicationSession/Runner
* fix: memory leak with Twisted/WebSocket, dropConnection and producer

18.10.1
-------

* Don't eat Component.stop() request when crossbar not connected (#1066)
* handle async on_progress callbacks properly (#1061)
* fix attribute error when ConnectionResetError does not contain "reason" attribute (#1059)
* infer rawsocket host, port from URL (#1056)
* fix error on connection lost if no reason (reason = None) (#1055)
* fixed typo on class name (#1054)

18.9.2
------

* fix: TLS error logging (#1052)


18.9.1
------

* new: Interrupt has Options.reason to signal detailed origin of call cancelation (active cancel vs passive timeout)
* fix: Cancel and Interrupt gets ``"killnowait"`` mode
* new: Cancel and Interrupt no longer have ``ABORT/"abort"``


18.8.2
------

* new: WAMP call cancel support
* fix: getting started documentation and general docs improvements
* fix: WebSocket auto-reconnect on opening handshake failure
* fix: more Python 3.7 compatibility and CI
* fix: Docker image building using multi-arch, size optimizations and more
* fix: asyncio failed to re-connect under some circumstances (#1040,
  #1041, #1010, #1030)


18.8.1
------

* fix: Python 3.7 compatibility
* fix: remove Python 2.6 support leftovers
* new: getting started docker-based examples in matching with docs


18.7.1
------

* new: Python 3.7 supported and integrated into CI
* new: WAMP-SCRAM examples
* fix: glitches in WAMP-SCRAM


18.6.1
------

* fix: implement abort argument for asyncio in WebSocketAdapterProtocol._closeConnection (#1012)


18.5.2
------

* fix: security (DoS amplification): a WebSocket server with
  permessage-deflate turned on could be induced to waste extra memory
  through a "zip-bomb" style attack. Setting a max-message-size will
  now stop deflating compressed data when the max is reached (instead
  of consuming all compressed data first). This could be used by a
  malicious client to make the server waste much more memory than the
  bandwidth the client uses.


18.5.1
------

* fix: asyncio/rawsocket buffer processing
* fix: example failures due to pypy longer startup time (#996)
* fix: add on_welcome for AuthWampCra (#992)
* fix: make run() of multiple components work on Windows (#986)
* new: `max_retries` now defaults to -1 ("try forever")


18.4.1
------

* new: WAMP-SCRAM authentication
* new: native vector extensions (NVX)
* fix: improve choosereactor (#965, #963)
* new: lots of new and improved documentation, component API and more
* new: Docker image tooling now in this repo
* fix: "fatal errors" in Component (#977)
* fix: AIO/Component: create a new loop if already closed
* fix: kwarg keys sometimes are bytes on Python2 (#980)
* fix: various improvements to new component API


18.3.1
------

* fix: endpoint configuration error messages (#942)
* fix: various improvements to the new components API (including retries)
* fix: pass `unregisterProducer` through to twisted to complement `WebSocketAdapterProtocol.registerProducer` (#875)


17.10.1
-------

* fix: proxy support (#918)
* fix: ensure that a future is not done before rejecting it (#919)
* fix: don't try to reject cancelled futures within pending requests when closing the session


17.9.3
------

`Published 2017-09-23 <https://pypi.python.org/pypi/autobahn/17.9.3>`__

* new: user configurable backoff policy
* fix: close aio loop on exit
* fix: some component API cleanups
* fix: cryptosign on py2
* new: allow setting correlation_is_last message marker in WAMP messages from user code


17.9.2
------

`Published 2017-09-12 <https://pypi.python.org/pypi/autobahn/17.9.2>`__

* new: allow setting correlation URI and anchor flag in WAMP messages from user code
* fix: WebSocket proxy connect on Python 3 (unicode vs bytes bug)

17.9.1
------

`Published 2017-09-04 <https://pypi.python.org/pypi/autobahn/17.9.1>`__

* new: allow setting correlation ID in WAMP messages from user code
* fix: distribute LICENSE file in all distribution formats (using setup.cfg metadata)

17.8.1
------

`Published 2017-08-15 <https://pypi.python.org/pypi/autobahn/17.8.1>`__

* new: prefix= kwarg now available on ApplicationSession.register for runtime method names
* new: @wamp.register(None) will use the function-name as the URI
* new: correlation and uri attributes for WAMP message tracing

17.7.1
------

`Published 2017-07-21 <https://pypi.python.org/pypi/autobahn/17.7.1>`__

* new: lots of improvements of components API, including asyncio support

17.6.2
------

`Published 2017-06-24 <https://pypi.python.org/pypi/autobahn/17.6.2>`__

* new: force register option when joining realms
* fix: TLS options in components API

17.6.1
------

`Published 2017-06-07 <https://pypi.python.org/pypi/autobahn/17.6.1>`__

* new: allow components to pass WebSocket/RawSocket options
* fix: register/subscribe decorators support different URI syntax from what session.register and session.subscribe support
* new: allow for standard Crossbar a.c..d style pattern URIs to be used with Pattern
* new: dynamic authorizer example
* new: configurable log level in `ApplicationRunner.run` for asyncio
* fix: forward reason of hard dropping WebSocket connection in `wasNotCleanReason`

17.5.1
------

`Published 2017-05-01 <https://pypi.python.org/pypi/autobahn/17.5.1>`__

* new: switched to calendar-based release/version numbering
* new: WAMP event retention example and docs
* new: WAMP subscribe/register options on WAMP decorators
* fix: require all TLS dependencies on extra_require_encryption setuptools
* new: support for X-Forwarded-For HTTP header
* fix: ABC interface definitions where missing "self"

0.18.2
------

`Published 2017-04-14 <https://pypi.python.org/pypi/autobahn/0.18.2>`__

* new: payload codec API
* fix: make WAMP-cryptobox use new payload codec API
* fix: automatic binary conversation for JSON
* new: improvements to experimental component API

0.18.1
------

`Published 2017-03-28 <https://pypi.python.org/pypi/autobahn/0.18.1>`__

* fix: errback all user handlers for all WAMP requests still outstanding when session/transport is closed/lost
* fix: allow WebSocketServerProtocol.onConnect to return a Future/Deferred
* new: allow configuration of RawSocket serializer
* new: test all examples on both WebSocket and RawSocket
* fix: revert to default arg for Deny reason
* new: WAMP-RawSocket and WebSocket default settings for asyncio
* new: experimental component based API and new WAMP Session class

0.18.0
------

`Published 2017-03-26 <https://pypi.python.org/pypi/autobahn/0.18.0>`__

* fix: big docs cleanup and polish
* fix: docs for publisher black-/whitelisting based on authid/authrole
* fix: serialization for publisher black-/whitelisting based on authid/authrole
* new: allow to stop auto-reconnecting for Twisted ApplicationRunner
* fix: allow empty realms (router decides) for asyncio ApplicationRunner

0.17.2
------

`Published 2017-02-25 <https://pypi.python.org/pypi/autobahn/0.17.2>`__

* new: WAMP-cryptosign elliptic curve based authentication support for asyncio
* new: CI testing on Twisted 17.1
* new: controller/shared attributes on ComponentConfig

0.17.1
------

`Published 2016-12-29 <https://pypi.python.org/pypi/autobahn/0.17.1>`__

* new: demo MQTT and WAMP clients interoperating via Crossbar.io
* new: WAMP message attributes for message resumption
* new: improvements to experimental WAMP components API
* fix: Python 3.4.4+ when using asyncio

0.17.0
------

`Published 2016-11-30 <https://pypi.python.org/pypi/autobahn/0.17.0>`__

* new: WAMP PubSub event retention
* new: WAMP PubSub last will / testament
* new: WAMP PubSub acknowledged delivery
* fix: WAMP Session lifecycle - properly handle asynchronous `ApplicationSession.onConnect` for asyncio

0.16.1
------

`Published 2016-11-07 <https://pypi.python.org/pypi/autobahn/0.16.1>`__

* fix: inconsistency between `PublishOptions` and `Publish` message
* new: improve logging with dropped connections (eg due to timeouts)
* fix: various smaller asyncio fixes
* new: rewrite all examples for new Python 3.5 async/await syntax
* fix: copyrights transferred from Tavendo GmbH to Crossbar.io Technologies GmbH

0.16.0
------

`Published 2016-08-14 <https://pypi.python.org/pypi/autobahn/0.16.0>`__

* new: new `autobahn.wamp.component` API in experimental stage
* new: Ed25519 OpenSSH and OpenBSD signify key support
* fix: allow Py2 and async user code in `onConnect` callback of asyncio

0.15.0
------

`Published 2016-07-19 <https://pypi.python.org/pypi/autobahn/0.15.0>`__

* new: WAMP AP option: register with maximum concurrency
* new: automatic reconnect for WAMP clients ApplicationRunner on Twisted
* new: RawSocket support in WAMP clients using ApplicationRunner on Twisted
* new: Set WebSocket production settings on WAMP clients using ApplicationRunner on Twisted
* fix: `#715 <https://github.com/crossbario/autobahn-python/issues/715>`_ Py2/Py3 issue with WebSocket traffic logging
* new: allow WAMP factories to take classes OR instances of ApplicationSession
* fix: make WebSocketResource working on Twisted 16.3
* fix: remove some minified AutobahnJS from examples (makes distro packagers happy)
* new: WAMP-RawSocket transport for asyncio
* fix: `#691 <https://github.com/crossbario/autobahn-python/issues/691>`_ (**security**) If the `allowedOrigins` websocket option was set, the resulting matching was insufficient and would allow more origins than intended

0.14.1
------

`Published 2016-05-26 <https://pypi.python.org/pypi/autobahn/0.14.1>`__

* fix: unpinned Twisted version again
* fix: remove X-Powered-By header
* fix: removed decrecated args to ApplicationRunner

0.14.0
------

`Published 2016-05-01 <https://pypi.python.org/pypi/autobahn/0.14.0>`__

* new: use of batched/chunked timers to massively reduce CPU load with WebSocket auto-ping/pong
* new: support new UBJSON WAMP serialization format
* new: publish universal wheels
* fix: replaced `msgpack-python` with `u-msgpack-python`
* fix: some glitches with `eligible / exlude` when used with `authid / authrole`
* fix: some logging glitches
* fix: pin Twisted at 16.1.1 (for now)

0.13.1
------

`Published 2016-04-09 <https://pypi.python.org/pypi/autobahn/0.13.1>`__

* moved helper funs for WebSocket URL handling to ``autobahn.websocket.util``
* fix: marshal WAMP options only when needed
* fix: various smallish examples fixes

0.13.0
------

`Published 2016-03-15 <https://pypi.python.org/pypi/autobahn/0.13.0>`__

* fix: better traceback logging (`#613 <https://github.com/crossbario/autobahn-python/pull/613>`_)
* fix: unicode handling in debug messages (`#606 <https://github.com/crossbario/autobahn-python/pull/606>`_)
* fix: return Deferred from ``run()`` (`#603 <https://github.com/crossbario/autobahn-python/pull/603>`_).
* fix: more debug logging improvements
* fix: more `Pattern` tests, fix edge case (`#592 <https://github.com/crossbario/autobahn-python/pull/592>`_).
* fix: better logging from ``asyncio`` ApplicationRunner
* new: ``disclose`` becomes a strict router-side feature (`#586 <https://github.com/crossbario/autobahn-python/issues/586>`_).
* new: subscriber black/whitelisting using authid/authrole
* new: asyncio websocket testee
* new: refine Observable API (`#593 <https://github.com/crossbario/autobahn-python/pull/593>`_).


0.12.1
------

`Published 2016-01-30 <https://pypi.python.org/pypi/autobahn/0.12.0>`__

* new: support CBOR serialization in WAMP
* new: support WAMP payload transparency
* new: beta version of WAMP-cryptosign authentication method
* new: alpha version of WAMP-cryptobox end-to-end encryption
* new: support user provided authextra data in WAMP authentication
* new: support WAMP channel binding
* new: WAMP authentication util functions for TOTP
* fix: support skewed time leniency for TOTP
* fix: use the new logging system in WAMP implementation
* fix: some remaining Python 3 issues
* fix: allow WAMP prefix matching register/subscribe with dot at end of URI

0.11.0
------

`Published 2015-12-09 <https://pypi.python.org/pypi/autobahn/0.11.0>`__

0.10.9
------

`Published 2015-09-15 <https://pypi.python.org/pypi/autobahn/0.10.8>`__

* fixes regression #500 introduced with commit 9f68749

0.10.8
------

`Published 2015-09-13 <https://pypi.python.org/pypi/autobahn/0.10.8>`__

* maintenance release with some issues fixed

0.10.7
------

`Published 2015-09-06 <https://pypi.python.org/pypi/autobahn/0.10.7>`__

* fixes a regression in 0.10.6

0.10.6
------

`Published 2015-09-05 <https://pypi.python.org/pypi/autobahn/0.10.6>`__

* maintenance release with nearly two dozen fixes
* improved Python 3, error logging, WAMP connection mgmt, ..

0.10.5
------

`Published 2015-08-06 <https://pypi.python.org/pypi/autobahn/0.10.5>`__

* maintenance release with lots of smaller bug fixes

0.10.4
------

`Published 2015-05-08 <https://pypi.python.org/pypi/autobahn/0.10.4>`__

* maintenance release with some smaller bug fixes

0.10.3
------

`Published 2015-04-14 <https://pypi.python.org/pypi/autobahn/0.10.3>`__

* new: using txaio package
* new: revised WAMP-over-RawSocket specification implemented
* fix: ignore unknown attributes in WAMP Options/Details

0.10.2
------

`Published 2015-03-19 <https://pypi.python.org/pypi/autobahn/0.10.2>`__

* fix: Twisted 11 lacks IPv6 address class
* new: various improvements handling errors from user code
* new: add parameter to limit max connections on WebSocket servers
* new: use new-style classes everywhere
* new: moved package content to repo root
* new: implement router revocation signaling for registrations/subscriptions
* new: a whole bunch of more unit tests / coverage
* new: provide reason/message when transport is lost
* fix: send WAMP errors upon serialization errors

0.10.1
------

`Published 2015-03-01 <https://pypi.python.org/pypi/autobahn/0.10.1>`__

* support for pattern-based subscriptions and registrations
* support for shared registrations
* fix: HEARTBEAT removed

0.10.0
------

`Published 2015-02-19 <https://pypi.python.org/pypi/autobahn/0.10.0>`__

* Change license from Apache 2.0 to MIT
* fix file line endings
* add setuptools test target
* fix Python 2.6

0.9.6
-----

`Published 2015-02-13 <https://pypi.python.org/pypi/autobahn/0.9.6>`__

* PEP8 code conformance
* PyFlakes code quality
* fix: warning for xrange on Python 3
* fix: parsing of IPv6 host headers
* add WAMP/Twisted service
* fix: handle connect error in ApplicationRunner (on Twisted)

0.9.5
-----

`Published 2015-01-11 <https://pypi.python.org/pypi/autobahn/0.9.5>`__

* do not try to fire onClose on a session that never existed in the first place (fixes #316)
* various doc fixes
* fix URI decorator component handling (PR #309)
* fix "standalone" argument to ApplicationRunner

0.9.4
-----

`Published 2014-12-15 <https://pypi.python.org/pypi/autobahn/0.9.4>`__

* refactor router code to Crossbar.io
* fix: catch error when Nagle cannot be set on stream transport (UDS)
* fix: spelling in doc strings / docs
* fix: WAMP JSON serialization of Unicode for ujson
* fix: Twisted plugins issue

0.9.3-2
-------

`Published 2014-11-15 <https://pypi.python.org/pypi/autobahn/0.9.3-2>`__

* maintenance release with some smaller bug fixes
* use ujson for WAMP when available
* reduce WAMP ID space to [0, 2**31-1]
* deactivate Twisted plugin cache recaching in `setup.py`

0.9.3
------
`Published 2014-11-10 <https://pypi.python.org/pypi/autobahn/0.9.3>`__

* feature: WebSocket origin checking
* feature: allow to disclose caller transport level info
* fix: Python 2.6 compatibility
* fix: handling of WebSocket close frame in a corner-case

0.9.2
------
`Published 2014-10-17 <https://pypi.python.org/pypi/autobahn/0.9.2>`__

* fix: permessage-deflate "client_max_window_bits" parameter handling
* fix: cancel opening handshake timeouts also for WebSocket clients
* feature: add more control parameters to Flash policy file factory
* feature: update AutobahnJS in examples
* feature: allow to set WebSocket HTTP headers via dict
* fix: ayncio imports for Python 3.4.2
* feature: added reconnecting WebSocket client example

0.9.1
------
`Published 2014-09-22 <https://pypi.python.org/pypi/autobahn/0.9.1>`__

* maintenance release with some smaller bug fixes

0.9.0
------
`Published 2014-09-02 <https://pypi.python.org/pypi/autobahn/0.9.0>`__

* all WAMP v1 code removed
* migrated various WAMP examples to WAMP v2
* improved unicode/bytes handling
* lots of code quality polishment
* more unit test coverage

0.8.15
------
`Published 2014-08-23 <https://pypi.python.org/pypi/autobahn/0.8.15>`__

* docs polishing
* small fixes (unicode handling and such)

0.8.14
------
`Published 2014-08-14 <https://pypi.python.org/pypi/autobahn/0.8.14>`__

* add automatic WebSocket ping/pong (#24)
* WAMP-CRA client side (beta!)

0.8.13
--------
`Published 2014-08-05 <https://pypi.python.org/pypi/autobahn/0.8.13>`__

* fix Application class (#240)
* support WSS for Application class
* remove implicit dependency on bzip2 (#244)

0.8.12
------
`Published 2014-07-23 <https://pypi.python.org/pypi/autobahn/0.8.12>`__

* WAMP application payload validation hooks
* added Tox based testing for multiple platforms
* code quality fixes

0.8.11
------
`Published <https://pypi.python.org/pypi/autobahn/0.8.11>`__

* hooks and infrastructure for WAMP2 authorization
* new examples: Twisted Klein, Crochet, wxPython
* improved WAMP long-poll transport
* improved stats tracker

0.8.10
------
`Published <https://pypi.python.org/pypi/autobahn/0.8.10>`__

* WAMP-over-Long-poll (preliminary)
* WAMP Authentication methods CR, Ticket, TOTP (preliminary)
* WAMP App object (preliminary)
* various fixes

0.8.9
-----
`Published <https://pypi.python.org/pypi/autobahn/0.8.9>`__

* maintenance release

0.8.8
-----
`Published <https://pypi.python.org/pypi/autobahn/0.8.8>`__

* initial support for WAMP on asyncio
* new WAMP examples
* WAMP ApplicationRunner

0.8.7
-----
`Published <https://pypi.python.org/pypi/autobahn/0.8.7>`__

* maintenance release

0.8.6
-----
`Published <https://pypi.python.org/pypi/autobahn/0.8.6>`__

* started reworking docs
* allow factories to operate without WS URL
* fix behavior on second protocol violation

0.8.5
-----
`Published <https://pypi.python.org/pypi/autobahn/0.8.5>`__

* support WAMP endpoint/handler decorators
* new examples for endpoint/handler decorators
* fix excludeMe pubsub option

0.8.4
-----
`Published <https://pypi.python.org/pypi/autobahn/0.8.4>`__

* initial support for WAMP v2 authentication
* various fixes/improvements to WAMP v2 implementation
* new example: WebSocket authentication with Mozilla Persona
* polish up documentation

0.8.3
-----
`Published <https://pypi.python.org/pypi/autobahn/0.8.3>`__

* fix bug with closing router app sessions

0.8.2
-----
`Published <https://pypi.python.org/pypi/autobahn/0.8.2>`__

* compatibility with latest WAMP v2 spec ("RC-2, 2014/02/22")
* various smaller fixes

0.8.1
-----
`Published <https://pypi.python.org/pypi/autobahn/0.8.1>`__

* WAMP v2 basic router (broker + dealer) implementation
* WAMP v2 example set
* WAMP v2: decouple transports, sessions and routers
* support explicit (binary) subprotocol name for wrapping WebSocket factory
* fix dependency on MsgPack

0.8.0
-----
`Published <https://pypi.python.org/pypi/autobahn/0.8.0>`__

* new: complete WAMP v2 protocol implementation and API layer
* new: basic WAMP v2 router implementation
* existing WAMP v1 implementation renamed

0.7.4
-----
`Published <https://pypi.python.org/pypi/autobahn/0.7.4>`__

* fix WebSocket server HTML status page
* fix close reason string handling
* new "slowsquare" example
* Python 2.6 fixes

0.7.3
-----
`Published <https://pypi.python.org/pypi/autobahn/0.7.3>`__

* support asyncio on Python 2 (via "Trollius" backport)

0.7.2
-----
`Published <https://pypi.python.org/pypi/autobahn/0.7.2>`__

* really fix setup/packaging

0.7.1
-----
`Published <https://pypi.python.org/pypi/autobahn/0.7.1>`__

* setup fixes
* fixes for Python2.6

0.7.0
-----
`Published <https://pypi.python.org/pypi/autobahn/0.7.0>`__

* asyncio support
* Python 3 support
* support WebSocket (and WAMP) over Twisted stream endpoints
* support Twisted stream endpoints over WebSocket
* twistd stream endpoint forwarding plugin
* various new examples
* fix Flash policy factory

0.6.5
-----
`Published <https://pypi.python.org/pypi/autobahn/0.6.5>`__

* Twisted reactor is no longer imported on module level (but lazy)
* optimize pure Python UTF8 validator (10-20% speedup on PyPy)
* opening handshake traffic stats (per-open stats)
* add multi-core echo example
* fixes with examples of streaming mode
* fix zero payload in streaming mode

0.6.4
-----
`Published <https://pypi.python.org/pypi/autobahn/0.6.4>`__

* support latest `permessage-deflate` draft
* allow controlling memory level for `zlib` / `permessage-deflate`
* updated reference, moved docs to "Read the Docs"
* fixes #157 (a WAMP-CRA timing attack very, very unlikely to be exploitable, but anyway)

0.6.3
-----
`Published <https://pypi.python.org/pypi/autobahn/0.6.3>`__

* symmetric RPCs
* WebSocket compression: client and server, `permessage-deflate`, `permessage-bzip2` and `permessage-snappy`
* `onConnect` is allowed to return Deferreds now
* custom publication and subscription handler are allowed to return Deferreds now
* support for explicit proxies
* default protocol version now is RFC6455
* option to use salted passwords for authentication with WAMP-CRA
* automatically use `ultrajson` acceleration package for JSON processing when available
* automatically use `wsaccel` acceleration package for WebSocket masking and UTF8 validation when available
* allow setting and getting of custom HTTP headers in WebSocket opening handshake
* various new code examples
* various documentation fixes and improvements

0.5.14
------
`Published <https://pypi.python.org/pypi/autobahn/0.5.14>`__

* base version when we started to maintain a changelog
