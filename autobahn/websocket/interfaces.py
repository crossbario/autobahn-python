###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

import abc
import six

__all__ = ('IWebSocketChannel',
           'IWebSocketChannelFrameApi',
           'IWebSocketChannelStreamingApi')


@six.add_metaclass(abc.ABCMeta)
class IWebSocketChannel(object):
    """
    A WebSocket channel is a bidirectional, full-duplex, ordered, reliable message channel
    over a WebSocket connection as specified in RFC6455.

    This interface defines a message-based API to WebSocket plus auxiliary hooks
    and methods.
    """

    @abc.abstractmethod
    def on_connect(self, request_or_response):
        """
        Callback fired during WebSocket opening handshake when a client connects (to a server with
        request from client) or when server connection established (by a client with response from
        server). This method may run asynchronous code.

        :param request_or_response: Connection request (for servers) or response (for clients).
        :type request_or_response: Instance of :class:`autobahn.websocket.types.ConnectionRequest`
           or :class:`autobahn.websocket.types.ConnectionResponse`.

        :returns:
           When this callback is fired on a WebSocket server, you may return either ``None`` (in
           which case the connection is accepted with no specific WebSocket subprotocol) or
           an instance of :class:`autobahn.websocket.types.ConnectionAccept`.
           When the callback is fired on a WebSocket client, this method must return ``None``.
           Do deny a connection, raise an Exception.
           You can also return a Deferred/Future that resolves/rejects to the above.
        """

    @abc.abstractmethod
    def on_open(self):
        """
        Callback fired when the initial WebSocket opening handshake was completed.
        You now can send and receive WebSocket messages.
        """

    @abc.abstractmethod
    def send_message(self, message):
        """
        Send a WebSocket message over the connection to the peer.

        :param message: The WebSocket message to be sent.
        :type message: Instance of :class:`autobahn.websocket.types.OutgoingMessage`
        """

    @abc.abstractmethod
    def on_message(self, message):
        """
        Callback fired when a complete WebSocket message was received.

        :param message: The WebSocket message received.
        :type message: :class:`autobahn.websocket.types.IncomingMessage`
        """

    @abc.abstractmethod
    def send_close(self, code=None, reason=None):
        """
        Starts a WebSocket closing handshake tearing down the WebSocket connection.

        :param code: An optional close status code (``1000`` for normal close or ``3000-4999`` for
           application specific close).
        :type code: int
        :param reason: An optional close reason (a string that when present, a status
           code MUST also be present).
        :type reason: unicode
        """

    @abc.abstractmethod
    def on_close(self, was_clean, code, reason):
        """
        Callback fired when the WebSocket connection has been closed (WebSocket closing
        handshake has been finished or the connection was closed uncleanly).

        :param wasClean: ``True`` iff the WebSocket connection was closed cleanly.
        :type wasClean: bool
        :param code: Close status code as sent by the WebSocket peer.
        :type code: int or None
        :param reason: Close reason as sent by the WebSocket peer.
        :type reason: unicode or None
        """

    @abc.abstractmethod
    def sendPreparedMessage(self, preparedMsg):
        """
        Send a message that was previously prepared with :func:`autobahn.websocket.protocol.WebSocketFactory.prepareMessage`.

        :param prepareMessage: A previously prepared message.
        :type prepareMessage: Instance of :class:`autobahn.websocket.protocol.PreparedMessage`.
        """

    @abc.abstractmethod
    def send_ping(self, payload=None):
        """
        Send a WebSocket ping to the peer.

        A peer is expected to pong back the payload a soon as "practical". When more than
        one ping is outstanding at a peer, the peer may elect to respond only to the last ping.

        :param payload: An (optional) arbitrary payload of length **less than 126** octets.
        :type payload: bytes or None
        """

    @abc.abstractmethod
    def on_ping(self, payload):
        """
        Callback fired when a WebSocket ping was received. A default implementation responds
        by sending a WebSocket pong.

        :param payload: Payload of ping (when there was any). Can be arbitrary, up to `125` octets.
        :type payload: bytes
        """

    @abc.abstractmethod
    def send_pong(self, payload=None):
        """
        Send a WebSocket pong to the peer.

        A WebSocket pong may be sent unsolicited. This serves as a unidirectional heartbeat.
        A response to an unsolicited pong is "not expected".

        :param payload: An (optional) arbitrary payload of length < 126 octets.
        :type payload: bytes
        """

    @abc.abstractmethod
    def on_pong(self, payload):
        """
        Callback fired when a WebSocket pong was received. A default implementation does nothing.

        :param payload: Payload of pong (when there was any). Can be arbitrary, up to 125 octets.
        :type payload: bytes
        """


class IWebSocketChannelFrameApi(IWebSocketChannel):
    """
    Frame-based API to a WebSocket channel.
    """

    @abc.abstractmethod
    def onMessageBegin(self, isBinary):
        """
        Callback fired when receiving of a new WebSocket message has begun.

        :param isBinary: ``True`` if payload is binary, else the payload is UTF-8 encoded text.
        :type isBinary: bool
        """

    @abc.abstractmethod
    def onMessageFrame(self, payload):
        """
        Callback fired when a complete WebSocket message frame for a previously begun
        WebSocket message has been received.

        :param payload: Message frame payload (a list of chunks received).
        :type payload: list of bytes
        """

    @abc.abstractmethod
    def onMessageEnd(self):
        """
        Callback fired when a WebSocket message has been completely received (the last
        WebSocket frame for that message has been received).
        """

    @abc.abstractmethod
    def beginMessage(self, isBinary=False, doNotCompress=False):
        """
        Begin sending a new WebSocket message.

        :param isBinary: ``True`` if payload is binary, else the payload must be UTF-8 encoded text.
        :type isBinary: bool
        :param doNotCompress: If ``True``, never compress this message. This only applies to
           Hybi-Mode and only when WebSocket compression has been negotiated on the WebSocket
           connection. Use when you know the payload incompressible (e.g. encrypted or
           already compressed).
        :type doNotCompress: bool
        """

    @abc.abstractmethod
    def sendMessageFrame(self, payload, sync=False):
        """
        When a message has been previously begun, send a complete message frame in one go.

        :param payload: The message frame payload. When sending a text message, the payload must
                        be UTF-8 encoded already.
        :type payload: bytes
        :param sync: If ``True``, try to force data onto the wire immediately.

           .. warning::
              Do NOT use this feature for normal applications.
              Performance likely will suffer significantly.
              This feature is mainly here for use by Autobahn|Testsuite.
        :type sync: bool
        """

    @abc.abstractmethod
    def endMessage(self):
        """
        End a message previously begun message. No more frames may be sent (for that message).
        You have to begin a new message before sending again.
        """


class IWebSocketChannelStreamingApi(IWebSocketChannelFrameApi):
    """
    Streaming API to a WebSocket channel.
    """

    @abc.abstractmethod
    def onMessageFrameBegin(self, length):
        """
        Callback fired when receiving a new message frame has begun.
        A default implementation will prepare to buffer message frame data.

        :param length: Payload length of message frame which is subsequently received.
        :type length: int
        """

    @abc.abstractmethod
    def onMessageFrameData(self, payload):
        """
        Callback fired when receiving data within a previously begun message frame.
        A default implementation will buffer data for frame.

        :param payload: Partial payload for message frame.
        :type payload: bytes
        """

    @abc.abstractmethod
    def onMessageFrameEnd(self):
        """
        Callback fired when a previously begun message frame has been completely received.
        A default implementation will flatten the buffered frame data and
        fire `onMessageFrame`.
        """

    @abc.abstractmethod
    def beginMessageFrame(self, length):
        """
        Begin sending a new message frame.

        :param length: Length of the frame which is to be started. Must be less or equal **2^63**.
        :type length: int
        """

    @abc.abstractmethod
    def sendMessageFrameData(self, payload, sync=False):
        """
        Send out data when within a message frame (message was begun, frame was begun).
        Note that the frame is automatically ended when enough data has been sent.
        In other words, there is no ``endMessageFrame``, since you have begun the frame
        specifying the frame length, which implicitly defined the frame end. This is different
        from messages, which you begin *and* end explicitly , since a message can contain
        an unlimited number of frames.

        :param payload: Frame payload to send.
        :type payload: bytes
        :param sync: If ``True``, try to force data onto the wire immediately.

           .. warning::
              Do NOT use this feature for normal applications.
              Performance likely will suffer significantly.
              This feature is mainly here for use by Autobahn|Testsuite.
        :type sync: bool

        :returns: When the currently sent message frame is still incomplete, returns octets
           remaining to be sent. When the frame is complete, returns **0**. Otherwise the amount
           of unconsumed data in payload argument is returned.
        :rtype: int
        """
