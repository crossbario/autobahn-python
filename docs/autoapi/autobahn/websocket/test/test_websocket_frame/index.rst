:mod:`autobahn.websocket.test.test_websocket_frame`
===================================================

.. py:module:: autobahn.websocket.test.test_websocket_frame


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.websocket.test.test_websocket_frame.create_client_frame


.. function:: create_client_frame(b64patch, **kwargs)

   Kind-of hack-y; maybe better to re-factor the Protocol to have a
   frame-encoder method-call? Anyway, makes a throwaway protocol
   encode a frame for us, collects the .sendData call and returns
   the data that would have gone out. Accepts all the kwargs that
   WebSocketClientProtocol.sendFrame() accepts.


