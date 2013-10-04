# AutobahnPython: Changelog

## v0.6.2
 * WebSocket compression, client and server, `permessage-deflate`, `permessage-bzip2`and `permessage-snappy`
 * `onConnect` is allowed to return Deferreds now
 * symmetric RPCs (server-to-client calls)
 * support for explicit proxies
 * default protocol version now is RFC6455
 * various new code examples
 * various documentation fixes and improvements
 * option to use salted passwords for authentication with WAMP-CRA
 * automatically use `ultrajson` acceleration package for JSON processing when available
 * automatically use `wsaccel` acceleration package for WebSocket masking and UTF8 validation when available
 * allow setting and getting of custom HTTP headers in WebSocket opening handshake

## v0.5.14
 * base version when we started to maintain a changelog