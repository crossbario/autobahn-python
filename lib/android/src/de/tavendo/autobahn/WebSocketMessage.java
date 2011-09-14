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

public class WebSocketMessage {

   public static class ClientHandshake {
      
      public String mHost;
      public String mPath;
      public String mOrigin;
      
      ClientHandshake() {         
      }
      
      ClientHandshake(String host, String path, String origin) {
         mHost = host;
         mPath = path;
         mOrigin = origin;
      }
   }
   
   public static class TextMessage {
      
      public String mPayload;
      
      TextMessage(String payload) {
         mPayload = payload;
      }
   }

   public static class BinaryMessage {
      
      public byte[] mPayload;
      
      BinaryMessage(byte[] payload) {
         mPayload = payload;
      }
   }

   public static class Close {
      
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

   public static class Ping {
      
      public byte[] mPayload;
      
      Ping() {
         mPayload = null;
      }
      
      Ping(byte[] payload) {
         mPayload = payload;
      }
   }

   public static class Pong {
      
      public byte[] mPayload;
      
      Pong() {
         mPayload = null;
      }
      
      Pong(byte[] payload) {
         mPayload = payload;
      }
   }

}
