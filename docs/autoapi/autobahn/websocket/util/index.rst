:mod:`autobahn.websocket.util`
==============================

.. py:module:: autobahn.websocket.util


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.websocket.util.create_url
   autobahn.websocket.util.parse_url


.. function:: create_url(hostname, port=None, isSecure=False, path=None, params=None)

   Create a WebSocket URL from components.

   :param hostname: WebSocket server hostname (for TCP/IP sockets) or
       filesystem path (for Unix domain sockets).
   :type hostname: str

   :param port: For TCP/IP sockets, WebSocket service port or ``None`` (to select default
       ports ``80`` or ``443`` depending on ``isSecure``. When ``hostname=="unix"``,
       this defines the path to the Unix domain socket instead of a TCP/IP network socket.
   :type port: int or str

   :param isSecure: Set ``True`` for secure WebSocket (``wss`` scheme).
   :type isSecure: bool

   :param path: WebSocket URL path of addressed resource (will be
       properly URL escaped). Ignored for RawSocket.
   :type path: str

   :param params: A dictionary of key-values to construct the query
       component of the addressed WebSocket resource (will be properly URL
       escaped). Ignored for RawSocket.
   :type params: dict

   :returns: Constructed WebSocket URL.
   :rtype: str


.. function:: parse_url(url)

   Parses as WebSocket URL into it's components and returns a tuple:

    - ``isSecure`` is a flag which is ``True`` for ``wss`` URLs.
    - ``host`` is the hostname or IP from the URL.

   and for TCP/IP sockets:

    - ``tcp_port`` is the port from the URL or standard port derived from
      scheme (``rs`` => ``80``, ``rss`` => ``443``).

   or for Unix domain sockets:

    - ``uds_path`` is the path on the local host filesystem.

   :param url: A valid WebSocket URL, i.e. ``ws://localhost:9000`` for TCP/IP sockets or
       ``ws://unix:/tmp/file.sock`` for Unix domain sockets (UDS).
   :type url: str

   :returns: A 6-tuple ``(isSecure, host, tcp_port, resource, path, params)`` (TCP/IP) or
       ``(isSecure, host, uds_path, resource, path, params)`` (UDS).
   :rtype: tuple


