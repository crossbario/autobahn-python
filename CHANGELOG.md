# Autobahn|Python Changelog

## v0.8.5
 * support endpoint/handler decorators
 * new examples for endpoint/handler deorators
 * fix excludeMe pubsub option

## v0.8.4
 * initial support for WAMP v2 authentication
 * various fixes/improvements to WAMP v2 implementation
 * new example: WebSocket auth. with Mozilla Persona
 * polish up documentation

## v0.8.3
 * fix bug with closing router app sessions

## v0.8.2
 * compatibility with latest WAMP v2 spec ("RC-2, 2014/02/22")
 * various smaller fixes

## v0.8.1
 * WAMP v2 basic router (broker + dealer) implementation
 * WAMP v2 example set
 * WAMP v2: decouple transports, sessions and routers
 * support explicit (binary) subprotocol name for wrapping WebSocket factory 
 * fix dependency on MsgPack

## v0.8.0
 * new: complete WAMP v2 protocol implementation and API layer
 * new: basic WAMP v2 router implementation
 * existing WAMP v1 implementation renamed

## v0.7.4
 * fix WebSocket server HTML status page
 * fix close reason string handling
 * new "slowsquare" example
 * Python 2.6 fixes

## v0.7.3
 * support asyncio on Python 2 (via "Trollius" backport)

## v0.7.2
 * really fix setup/packaging

## v0.7.1
 * setup fixes
 * fixes for Python2.6

## v0.7.0
 * asyncio support
 * Python 3 support
 * support WebSocket (and WAMP) over Twisted stream endpoints
 * support Twisted stream endpoints over WebSocket
 * twistd stream endpoint forwarding plugin
 * various new examples
 * fix Flash policy factory

## v0.6.5
 * Twisted reactor is no longer imported on module level (but lazy)
 * optimize pure Python UTF8 validator (10-20% speedup on PyPy)
 * opening handshake traffic stats (per-open stats)
 * add multicore echo example
 * fixes with examples of streaming mode
 * fix zero payload in streaming mode

## v0.6.4
 * support latest `permessage-deflate` [draft](http://tools.ietf.org/html/draft-ietf-hybi-permessage-compression-15)
 * allow controlling memory level for zlib / `permessage-deflate`
 * updated reference, moved to [Readthedocs](https://autobahnpython.readthedocs.org/)
 * fixes #157 (a WAMP-CRA timing attack - very, very unlikely to be exploitable, but anyway)

## v0.6.3
 * [symmetric RPCs](https://github.com/tavendo/AutobahnPython/tree/master/examples/wamp/rpc/symmetric) (server-to-client calls)
 * [WebSocket compression](http://tools.ietf.org/html/draft-ietf-hybi-permessage-compression), client and server, `permessage-deflate`, `permessage-bzip2`and `permessage-snappy`
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

## v0.5.14
 * base version when we started to maintain a changelog
