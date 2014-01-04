# AutobahnPython: Changelog

## v0.7.1
 * setup fixes
 * fixes for Python2.6

## v0.7.0
 * asyncio support
 * Python 3 support
 * initial support for WAMPv2
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
