:mod:`autobahn.exception`
=========================

.. py:module:: autobahn.exception


Module Contents
---------------

.. exception:: PayloadExceededError


   Bases: :class:`RuntimeError`

   Exception raised when the serialized and framed (eg WebSocket/RawSocket) WAMP payload
   exceeds the transport message size limit.


