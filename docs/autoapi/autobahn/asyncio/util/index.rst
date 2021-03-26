:mod:`autobahn.asyncio.util`
============================

.. py:module:: autobahn.asyncio.util


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.asyncio.util.transport_channel_id
   autobahn.asyncio.util.peer2str
   autobahn.asyncio.util.get_serializers


.. data:: __all
   :annotation: = ['sleep', 'peer2str', 'transport_channel_id']

   

.. function:: transport_channel_id(transport, is_server: bool, channel_id_type: Optional[str] = None) -> bytes

   Application-layer user authentication protocols are vulnerable to generic
   credential forwarding attacks, where an authentication credential sent by
   a client C to a server M may then be used by M to impersonate C at another
   server S. To prevent such credential forwarding attacks, modern authentication
   protocols rely on channel bindings. For example, WAMP-cryptosign can use
   the tls-unique channel identifier provided by the TLS layer to strongly bind
   authentication credentials to the underlying channel, so that a credential
   received on one TLS channel cannot be forwarded on another.

   :param transport: The asyncio TLS transport to extract the TLS channel ID from.
   :param is_server: Flag indicating the transport is for a server.
   :param channel_id_type: TLS channel ID type, currently only "tls-unique" is supported.
   :returns: The TLS channel id (32 bytes).


.. function:: peer2str(peer)


.. function:: get_serializers()


