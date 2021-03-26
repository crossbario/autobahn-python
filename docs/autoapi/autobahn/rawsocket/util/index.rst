:mod:`autobahn.rawsocket.util`
==============================

.. py:module:: autobahn.rawsocket.util


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.rawsocket.util.create_url
   autobahn.rawsocket.util.parse_url


.. function:: create_url(hostname, port=None, isSecure=False)

   Create a RawSocket URL from components.

   :param hostname: RawSocket server hostname (for TCP/IP sockets) or
       filesystem path (for Unix domain sockets).
   :type hostname: str

   :param port: For TCP/IP sockets, RawSocket service port or ``None`` (to select default
       ports ``80`` or ``443`` depending on ``isSecure``. When ``hostname=="unix"``,
       this defines the path to the Unix domain socket instead of a TCP/IP network socket.
   :type port: int or str

   :param isSecure: Set ``True`` for secure RawSocket (``rss`` scheme).
   :type isSecure: bool

   :returns: Constructed RawSocket URL.
   :rtype: str


.. function:: parse_url(url)

   Parses as RawSocket URL into it's components and returns a tuple:

    - ``isSecure`` is a flag which is ``True`` for ``rss`` URLs.
    - ``host`` is the hostname or IP from the URL.

   and for TCP/IP sockets:

    - ``tcp_port`` is the port from the URL or standard port derived from
      scheme (``rs`` => ``80``, ``rss`` => ``443``).

   or for Unix domain sockets:

    - ``uds_path`` is the path on the local host filesystem.

   :param url: A valid RawSocket URL, i.e. ``rs://localhost:9000`` for TCP/IP sockets or
       ``rs://unix:/tmp/file.sock`` for Unix domain sockets (UDS).
   :type url: str

   :returns: A 3-tuple ``(isSecure, host, tcp_port)`` (TCP/IP) or ``(isSecure, host, uds_path)`` (UDS).
   :rtype: tuple


