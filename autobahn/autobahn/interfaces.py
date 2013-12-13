###############################################################################
##
##  Copyright (C) 2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################


import zope
from zope.interface import Interface, Attribute


class IWebSocketChannel(Interface):
   """
   A WebSocket channel is a bidirectional, ordered, reliable message channel
   over a WebSocket connection as specified in RFC6455.
   """

   def onOpen():
      """
      Callback fired when the initial WebSocket opening handshake was completed.
      """

   def onMessage(payload, isBinary):
      """
      Callback fired when a complete message was received.

      :param payload: Message payload (UTF-8 encoded text string or binary string). Can also be empty, when message contained no payload.
      :type payload: str
      :param isBinary: If True, payload is binary, otherwise text (UTF-8 encoded).
      :type isBinary: bool
      """

   def sendMessage(payload, isBinary = False, fragmentSize = None, doNotCompress = False):
      """
      Send out a WebSocket message.

      You can send text or binary message, and optionally specifiy a payload fragment size.
      When the latter is given, the payload will be split up into WebSocket frames with
      payload <= the fragmentSize given.

      :param payload: The message payload. When sending a text message (`isBinary == False`), the payload must be UTF-8 encoded already.
      :type payload: binary or UTF-8 string
      :param isBinary: Flag to indicate payload type (`True == binary`).
      :type bool
      :param fragmentSize: Fragment message into WebSocket fragments of this size.
      :type fragmentSize: int
      :param doNotCompress: Iff `True`, never compress this message. This only applies to Hybi-Mode and if WebSocket compression has been negotiated on the WebSocket client-server connection. Use when you know the payload is not compressible (e.g. encrypted or already compressed).
      :type doNotCompress: bool
      """

   def sendClose(code = None, reason = None):
      """
      Starts a WebSocket closing handshake tearing down the WebSocket connection.

      :param code: An optional close status code (1000 for normal close or 3000-4999 for application defined close).
      :type code: int
      :param reason: An optional close reason (a UTF-8 encoded string that when present, a status code MUST also be present).
      :type reason: str
      """

   def onClose(wasClean, code, reason):
      """
      Callback fired when the WebSocket connection has been closed (WebSocket closing handshake finished).

      :param wasClean: True, iff the WebSocket connection was closed cleanly.
      :type wasClean: bool
      :param code: None or close status code (as sent by the WebSocket peer).
      :type code: int
      :param reason: None or close reason (as sent by the WebSocket peer) as UTF-8 encoded string.
      :type reason: str
      """



class IWebSocketChannelFrameApi(IWebSocketChannel):
   """
   Frame-based API to WebSocket channel.
   """

   def onMessageBegin(opcode):
      """
      Callback fired when receiving a new WebSocket message has begun.

      :param opcode: WebSocket frame opcode of message begun.
      :type opcode: int
      """

   def onMessageFrame(payload, reserved):
      """
      Callback fired when a complete WebSocket message frame for a previously begun
      WebSocket message has been received.

      :param payload: Message frame payload (a list of chunks received).
      :type payload: list of str
      :param reserved: Reserved bits set in WebSocket frame (an integer from 0 to 7).
      :type reserved: int
      """

   def onMessageEnd():
      """
      Callback fired when a WebSocket message has been completely received (the last
      WebSocket frame for that message has arrived)
      """

   def beginMessage(isBinary = False, doNotCompress = False):
      """
      Begin sending a new WebSocket message.

      :param binary: Flag to indicate payload type (`True == binary`).
      :type bool
      :param doNotCompress: Iff `True`, never compress this message. This only applies to Hybi-Mode and if WebSocket compression has been negotiated on the WebSocket client-server connection. Use when you know the payload is not compressible (e.g. encrypted or already compressed).
      :type doNotCompress: bool
      """

   def sendMessageFrame(self, payload, sync = False):
      """
      When a message has been previously begun with :meth:`autobahn.websocket.WebSocketProtocol.beginMessage`,
      send a complete message frame in one go.

      Modes: Hybi

      :param payload: The message payload. When sending a text message, the payload must be UTF-8 encoded already.
      :type payload: binary or UTF-8 string
      :param sync: Iff `True`, try to force message onto wire before sending more stuff. Note: do NOT use this normally, performance likely will suffer significantly. This feature is mainly here for use by the testsuite.
      :type sync: bool
      """

   def endMessage(self):
      """
      End a message previously begun with :meth:`autobahn.websocket.WebSocketProtocol.beginMessage`.
      No more frames may be sent (for that message). You have to begin a new message before sending again.

      Modes: Hybi, Hixie
      """



class IWebSocketChannelStreamingApi(IWebSocketChannelFrameApi):

   def onMessageFrameBegin(self, length, reserved):
      """
      Callback when receiving a new message frame has begun. Default implementation will
      prepare to buffer message frame data. Override in derived class.

      Modes: Hybi

      :param length: Payload length of message frame which is to be received.
      :type length: int
      :param reserved: Reserved bits set in frame (an integer from 0 to 7).
      :type reserved: int
      """

   def onMessageFrameData(self, payload):
      """
      Callback when receiving data witin message frame. Default implementation will
      buffer data for frame. Override in derived class.

      Modes: Hybi, Hixie

      Notes:
        - For Hixie mode, this method is slightly misnamed for historic reasons.

      :param payload: Partial payload for message frame.
      :type payload: str
      """

   def onMessageFrameEnd(self):
      """
      Callback when a message frame has been completely received. Default implementation
      will flatten the buffered frame data and callback onMessageFrame. Override
      in derived class.

      Modes: Hybi
      """

   def beginMessageFrame(self, length):
      """
      Begin sending new message frame.

      Modes: Hybi

      :param length: Length of frame which is started. Must be >= 0 and <= 2^63.
      :type length: int
      :param reserved: Reserved bits for frame (an integer from 0 to 7). Note that reserved != 0 is only legal when an extension has been negoiated which defines semantics.
      :type reserved: int
      :param mask: Optional frame mask. When given, this is used. When None and the peer is a client, a mask will be internally generated. For servers None is default.
      :type mask: str
      """

   def sendMessageFrameData(self, payload, sync = False):
      """
      Send out data when within message frame (message was begun, frame was begun).
      Note that the frame is automatically ended when enough data has been sent
      that is, there is no endMessageFrame, since you have begun the frame specifying
      the frame length, which implicitly defined the frame end. This is different from
      messages, which you begin and end, since a message can contain an unlimited number
      of frames.

      Modes: Hybi, Hixie

      Notes:
        - For Hixie mode, this method is slightly misnamed for historic reasons.

      :param payload: Data to send.

      :returns: int -- Hybi mode: when frame still incomplete, returns outstanding octets, when frame complete, returns <= 0, when < 0, the amount of unconsumed data in payload argument. Hixie mode: returns None.
      """



class IWampDealer(Interface):
   """
   """

   def register(self, endpoint, obj):
      """
      """

   def registerMethod(self, endpoint, obj, method):
      """
      """

   def registerProcedure(self, endpoint, procedure):
      """
      """

   def unregister(self, endpoint):
      """
      """


class IWampBroker(Interface):
   """
   """

   def register(self, topic, prefix = False, publish = True, subscribe = True):
      """
      """

   def unregister(self, topic):
      """
      """


class IWampPublishOptions(Interface):

   excludeMe = Attribute("Exclude me, the publisher, from receiving the event (even though I may be subscribed).")



class IWampSession(Interface):
   """
   """

   def call(self, *args):
      """
      """

   def subscribe(self, topic, handler):
      """
      """

   def unsubscribe(self, topic, handler = None):
      """
      """

   def publish(self, topic, event,
               excludeMe = None,
               exclude = None,
               eligible = None,
               discloseMe = None):
      """
      """

   def setDealer(self, dealer = None):
      """
      """

   def setBroker(self, broker = None):
      """
      """
