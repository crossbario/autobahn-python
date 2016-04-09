:tocdepth: 1

.. _changelog:

Changelog
=========

0.13.1
------

`Published 2016-04-09 <https://pypi.python.org/pypi/autobahn/0.13.1>`_

* moved helper funs for WebSocket URL handling to ``autobahn.websocket.util``
* fix: marshal WAMP options only when needed
* fix: various smallish examples fixes

0.13.0
------

`Published 2016-03-15 <https://pypi.python.org/pypi/autobahn/0.13.0>`_

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
