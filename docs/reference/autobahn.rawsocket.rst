Module ``autobahn.rawsocket``
=============================

WAMP-RawSocket is an alternative WAMP transport that has less overhead compared to WebSocket, and is vastly simpler to implement. It can run over any stream based underlying transport, such as TCP or Unix domain socket. However, it does NOT run into the browser.


RawSocket Utilities
-------------------

See :doc:`/autoapi/autobahn/rawsocket/util/index`.

RawSocket utilities that do not depend on the specific networking framework being used (Twisted or asyncio).
