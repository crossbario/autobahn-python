/******************************************************************************
 *
 *  Copyright 2011 Tavendo GmbH
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 ******************************************************************************/

package de.tavendo.autobahn;

/**
 * The master thread and the background reader/writer threads communicate
 * using these messages for WebSockets connections.
 */
public class WebSocketMessage {

   /// Base message class.
   public static class Message {

   }

   /// Initial WebSockets handshake (client request).
   public static class ClientHandshake extends Message {

      public String mHost;
      public String mPath;
      public String mQuery;
      public String mOrigin;

      ClientHandshake(String host) {
         mPath = "/";
         mOrigin = null;
      }

      ClientHandshake(String host, String path, String origin) {
         mHost = host;
         mPath = path;
         mOrigin = origin;
      }
   }

   /// Initial WebSockets handshake (server response).
   public static class ServerHandshake extends Message {

   }

   /// WebSockets connection lost
   public static class ConnectionLost extends Message {
   }

   /// WebSockets reader detected WS protocol violation.
   public static class ProtocolViolation extends Message {

      public WebSocketException mException;

      public ProtocolViolation(WebSocketException e) {
         mException = e;
      }
   }

   /// An exception occured in the WS reader or WS writer.
   public static class Error extends Message {

      public Exception mException;

      public Error(Exception e) {
         mException = e;
      }
   }

   public static class Quit extends Message {
   }

   /// WebSockets text message to send or received.
   public static class TextMessage extends Message {

      public String mPayload;

      TextMessage(String payload) {
         mPayload = payload;
      }
   }

   /// WebSockets raw (UTF-8) text message to send or received.
   public static class RawTextMessage extends Message{

      public byte[] mPayload;

      RawTextMessage(byte[] payload) {
         mPayload = payload;
      }
   }

   /// WebSockets binary message to send or received.
   public static class BinaryMessage extends Message{

      public byte[] mPayload;

      BinaryMessage(byte[] payload) {
         mPayload = payload;
      }
   }

   /// WebSockets close to send or received.
   public static class Close extends Message {

      public int mCode;
      public String mReason;

      Close() {
         mCode = -1;
         mReason = null;
      }

      Close(int code) {
         mCode = code;
         mReason = null;
      }

      Close(int code, String reason) {
         mCode = code;
         mReason = reason;
      }
   }

   /// WebSockets ping to send or received.
   public static class Ping extends Message {

      public byte[] mPayload;

      Ping() {
         mPayload = null;
      }

      Ping(byte[] payload) {
         mPayload = payload;
      }
   }

   /// WebSockets pong to send or received.
   public static class Pong extends Message {

      public byte[] mPayload;

      Pong() {
         mPayload = null;
      }

      Pong(byte[] payload) {
         mPayload = payload;
      }
   }

}
