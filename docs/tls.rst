.. _tls-channel-binding:

TLS Channel Binding
===================

Application-layer authentication protocols such as WAMP-cryptosign are vulnerable to
generic *credential forwarding* attacks: a credential a client ``C`` sends to a server
``M`` may be replayed by ``M`` to impersonate ``C`` at another server ``S``. **TLS
channel binding** defends against this by binding the authentication credential to the
underlying TLS channel, so a credential captured on one channel cannot be forwarded on
another.

AutobahnPython extracts a 32-byte *channel ID* from a TLS connection. Two binding types
are defined, split by TLS version:

* ``tls-unique`` (`RFC 5929 <https://www.rfc-editor.org/rfc/rfc5929.html>`_) — for
  **TLS <= 1.2**. The channel ID is ``sha256`` of the TLS *Finished* message. It is
  *asymmetric* (RFC 5929, section 3.1): in a full handshake the client uses its own
  Finished message and the server uses the peer's.
* ``tls-exporter`` (`RFC 9266 <https://www.rfc-editor.org/rfc/rfc9266.html>`_) — for
  **TLS 1.3**. The channel ID is exported keying material for the label
  ``EXPORTER-Channel-Binding`` (32 bytes, used raw, no hashing). It is *symmetric*
  (client and server derive the same value) and independent of session resumption.

AutobahnPython uses a **hard split**: ``tls-unique`` on TLS <= 1.2, ``tls-exporter`` on
TLS 1.3. ``tls-exporter`` on TLS 1.2 (RFC 9266 with Extended Master Secret) and
``tls-server-end-point`` are out of scope.

Backends
--------

The two networking backends use different TLS stacks, which determines what they can do:

* **Twisted** uses **pyOpenSSL**, which exposes ``export_keying_material()`` as well as
  ``get_finished()`` / ``get_peer_finished()`` — so Twisted supports **both**
  ``tls-unique`` and ``tls-exporter``. Crossbar.io runs on Twisted, so router and
  router-to-router (rlink) legs get TLS 1.3 + ``tls-exporter``.
* **asyncio** uses the Python **stdlib** ``ssl`` module, whose
  ``ssl.CHANNEL_BINDING_TYPES`` is ``['tls-unique']`` on every version through CPython
  3.14 — it does **not** expose ``tls-exporter``. On asyncio, ``tls-exporter`` raises
  ``NotImplementedError``. (Should a future CPython add ``tls-exporter`` to
  ``ssl.CHANNEL_BINDING_TYPES``, AutobahnPython uses it automatically.)

Support matrix
--------------

What ``transport_channel_id()`` returns for each backend, role and TLS scenario:

.. list-table::
   :header-rows: 1
   :stub-columns: 1
   :widths: 20 12 14 14 20 20

   * - Backend / role
     - No TLS
     - TLS 1.2, no binding
     - TLS 1.3, no binding
     - TLS 1.2 ``tls-unique``
     - TLS 1.3 ``tls-exporter``
   * - **Twisted** client
     - — [1]_
     - — [2]_
     - — [2]_
     - ✓ ``sha256(get_finished())``
     - ✓ ``export_keying_material``
   * - **Twisted** server
     - — [1]_
     - — [2]_
     - — [2]_
     - ✓ ``sha256(get_peer_finished())``
     - ✓ ``export_keying_material``
   * - **asyncio** client
     - — [1]_
     - — [2]_
     - — [2]_
     - ✓ ``sha256(get_channel_binding())``
     - ✗ ``NotImplementedError``
   * - **asyncio** server
     - — [1]_
     - — [2]_
     - — [2]_
     - ✓ ``sha256(get_channel_binding())``
     - ✗ ``NotImplementedError``

.. [1] Not a TLS transport: requesting a channel binding type raises; ``channel_id_type=None`` returns 32 NUL bytes.
.. [2] No binding requested (``channel_id_type=None``): the connection works, no channel ID is computed (32 NUL bytes).

On asyncio the stdlib handles the client/server role and resumption itself, so both roles
compute the same value. ``tls-unique`` on TLS 1.3 and ``tls-exporter`` on TLS 1.2 are not
supported combinations (the hard split above): requesting ``tls-unique`` on a TLS 1.3
connection **raises** (it is not a valid binding there — the TLS Finished message no
longer carries the needed semantics — and the underlying libraries would otherwise return
a non-standard value silently), so a TLS 1.3 peer uses ``tls-exporter`` (Twisted) or no
binding at all, never ``tls-unique`` (#2078).

Usage
-----

Channel binding is normally selected by WAMP-cryptosign via the ``channel_binding``
entry in ``HELLO.authextra``, and the extracted channel ID is also surfaced on
``TransportDetails.channel_id``. The channel ID can be extracted directly with
``transport_channel_id(transport, is_server, channel_id_type)``.

Twisted, extract ``tls-exporter`` on a TLS 1.3 connection:

.. code-block:: python

    from autobahn.twisted.util import transport_channel_id

    # `transport` is the connected, TLS-secured Twisted transport; is_server=False on a client
    channel_id = transport_channel_id(transport, is_server=False, channel_id_type="tls-exporter")
    assert len(channel_id) == 32

asyncio cannot do ``tls-exporter`` — handle the ``NotImplementedError`` (or use
``tls-unique`` on TLS <= 1.2, or switch to the Twisted backend):

.. code-block:: python

    from autobahn.asyncio.util import transport_channel_id

    try:
        channel_id = transport_channel_id(transport, is_server=False, channel_id_type="tls-exporter")
    except NotImplementedError:
        # stdlib ssl has no tls-exporter; use tls-unique (TLS <= 1.2) or the Twisted backend
        channel_id = transport_channel_id(transport, is_server=False, channel_id_type="tls-unique")

Reading the channel ID that AutobahnPython populates on the transport details:

.. code-block:: python

    # the key follows the negotiated TLS version (hard split): "tls-unique" on TLS <= 1.2,
    # "tls-exporter" on TLS 1.3 (Twisted); on asyncio there is no channel binding on TLS 1.3
    details = session._transport.transport_details
    channel_id = details.channel_id.get("tls-exporter") or details.channel_id.get(
        "tls-unique"
    )

.. note::

   The channel-ID *extraction* documented here is used by AutobahnPython to populate
   ``TransportDetails.channel_id`` by negotiated TLS version (``tls-unique`` on TLS <= 1.2,
   ``tls-exporter`` on TLS 1.3 where available, and nothing on asyncio TLS 1.3), and by
   WAMP-cryptosign, which selects and advertises the binding type from the negotiated TLS
   version and rejects ``tls-unique`` on TLS 1.3 (#1584, #2078).
