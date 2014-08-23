:tocdepth: 1

.. _changelog:

Changelog
=========

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
