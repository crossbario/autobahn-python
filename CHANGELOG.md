# AutobahnPython: Changelog

## v0.6.2
 * symmetric RPCs (server-to-client calls)
 * WebSocket compression, client and server, `permessage-deflate`, `permessage-bzip2`and `permessage-snappy`
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