:mod:`autobahn.wamp.serializer`
===============================

.. py:module:: autobahn.wamp.serializer


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.wamp.serializer.Serializer
   autobahn.wamp.serializer.JsonObjectSerializer
   autobahn.wamp.serializer.JsonSerializer



.. class:: Serializer(serializer)


   Bases: :class:`object`

   Base class for WAMP serializers. A WAMP serializer is the core glue between
   parsed WAMP message objects and the bytes on wire (the transport).

   .. attribute:: RATED_MESSAGE_SIZE
      :annotation: = 512

      Serialized WAMP message payload size per rated WAMP message.


   .. attribute:: MESSAGE_TYPE_MAP
      

      Mapping of WAMP message type codes to WAMP message classes.


   .. method:: stats_reset(self)

      Get serializer statistics: timestamp when statistics were last reset.

      :return: Last reset time of statistics (UTC, ns since Unix epoch)
      :rtype: int


   .. method:: stats_bytes(self)

      Get serializer statistics: bytes (serialized + unserialized).

      :return: Number of bytes.
      :rtype: int


   .. method:: stats_messages(self)

      Get serializer statistics: messages (serialized + unserialized).

      :return: Number of messages.
      :rtype: int


   .. method:: stats_rated_messages(self)

      Get serializer statistics: rated messages (serialized + unserialized).

      :return: Number of rated messages.
      :rtype: int


   .. method:: set_stats_autoreset(self, rated_messages, duration, callback, reset_now=False)

      Configure a user callback invoked when accumulated stats hit specified threshold.
      When the specified number of rated messages have been processed or the specified duration
      has passed, statistics are automatically reset, and the last statistics is provided to
      the user callback.

      :param rated_messages: Number of rated messages that should trigger an auto-reset.
      :type rated_messages: int

      :param duration: Duration in ns that when passed will trigger an auto-reset.
      :type duration: int

      :param callback: User callback to be invoked when statistics are auto-reset. The function
          will be invoked with a single positional argument: the accumulated statistics before the reset.
      :type callback: callable


   .. method:: stats(self, reset=True, details=False)

      Get (and reset) serializer statistics.

      :param reset: If ``True``, reset the serializer statistics.
      :type reset: bool

      :param details: If ``True``, return detailed statistics split up by serialization/unserialization.
      :type details: bool

      :return: Serializer statistics, eg:

          .. code-block:: json

              {
                  "timestamp": 1574156576688704693,
                  "duration": 34000000000,
                  "bytes": 0,
                  "messages": 0,
                  "rated_messages": 0
              }

      :rtype: dict


   .. method:: serialize(self, msg)

      Implements :func:`autobahn.wamp.interfaces.ISerializer.serialize`


   .. method:: unserialize(self, payload, isBinary=None)

      Implements :func:`autobahn.wamp.interfaces.ISerializer.unserialize`



.. class:: JsonObjectSerializer(batched=False, use_binary_hex_encoding=False)


   Bases: :class:`object`

   .. attribute:: JSON_MODULE
      

      The JSON module used (now only stdlib).


   .. attribute:: NAME
      :annotation: = json

      

   .. attribute:: BINARY
      :annotation: = False

      

   .. method:: serialize(self, obj)

      Implements :func:`autobahn.wamp.interfaces.IObjectSerializer.serialize`


   .. method:: unserialize(self, payload)

      Implements :func:`autobahn.wamp.interfaces.IObjectSerializer.unserialize`



.. class:: JsonSerializer(batched=False)


   Bases: :class:`autobahn.wamp.serializer.Serializer`

   Base class for WAMP serializers. A WAMP serializer is the core glue between
   parsed WAMP message objects and the bytes on wire (the transport).

   .. attribute:: SERIALIZER_ID
      :annotation: = json

      ID used as part of the WebSocket subprotocol name to identify the
      serializer with WAMP-over-WebSocket.


   .. attribute:: RAWSOCKET_SERIALIZER_ID
      :annotation: = 1

      ID used in lower four bits of second octet in RawSocket opening
      handshake identify the serializer with WAMP-over-RawSocket.


   .. attribute:: MIME_TYPE
      :annotation: = application/json

      MIME type announced in HTTP request/response headers when running
      WAMP-over-Longpoll HTTP fallback.



