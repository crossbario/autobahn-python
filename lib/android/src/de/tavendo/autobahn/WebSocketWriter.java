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

import java.io.IOException;
import java.nio.channels.SocketChannel;

import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.util.Base64;
import android.util.Log;
import java.util.Random;

/**
 * Transport Writer. This is run on own background thread with own message loop.
 */
public class WebSocketWriter extends Handler {
   
   private static final String TAG = "de.tavendo.autobahn.WebSocketWriter";

   private final ByteBufferOutputStream mBufferStream;
   private final SocketChannel mConnection;
   private final Random mRng = new Random();

   
   public static class WebSocketClientHandshake {
      
      public String mHost;
      public String mPath;
      public String mOrigin;
      
      WebSocketClientHandshake() {         
      }
      
      WebSocketClientHandshake(String host, String path, String origin) {
         mHost = host;
         mPath = path;
         mOrigin = origin;
      }
   }
   
   public static class WebSocketTextMessage {
      
      public String mPayload;
      
      WebSocketTextMessage(String payload) {
         mPayload = payload;
      }
   }

   public WebSocketWriter(Looper looper, SocketChannel connection) {

      super(looper);
      
      mConnection = connection;
      mBufferStream = new ByteBufferOutputStream();
   }

   private String createWsKey() {
      byte[] ba = new byte[16];
      mRng.nextBytes(ba);
      return Base64.encodeToString(ba, Base64.DEFAULT);
   }
   

   public void forwardMessage(Object obj) {
      
      Message msg = obtainMessage();
      msg.obj = obj;
      sendMessage(msg);
   }

   @Override
   public void handleMessage(Message msg) {

      try {

         mBufferStream.clear();

         if (msg.obj instanceof WebSocketTextMessage) {
            
            WebSocketTextMessage textMessage = (WebSocketTextMessage) msg.obj;
            mBufferStream.write(textMessage.mPayload);
            
         } else if (msg.obj instanceof WebSocketClientHandshake) {
            
            WebSocketClientHandshake clientHandshakeMessage = (WebSocketClientHandshake) msg.obj;
            
            mBufferStream.write("GET " + clientHandshakeMessage.mPath + " HTTP/1.1");
            mBufferStream.crlf();
            mBufferStream.write("Host: " + clientHandshakeMessage.mHost);
            mBufferStream.crlf();
            mBufferStream.write("Upgrade: websocket");
            mBufferStream.crlf();
            mBufferStream.write("Connection: Upgrade");
            mBufferStream.crlf();
            mBufferStream.write("Sec-WebSocket-Key: " + createWsKey());
            mBufferStream.crlf();
            if (clientHandshakeMessage.mOrigin != null && !clientHandshakeMessage.mOrigin.equals("")) {
               mBufferStream.write("Origin: " + clientHandshakeMessage.mOrigin);
               mBufferStream.crlf();
            }
            mBufferStream.write("Sec-WebSocket-Version: 13");
            mBufferStream.crlf();
            mBufferStream.crlf();
            
         } else {
            
            throw new WebSocketException("invalid message to WebSocketWriter");
            
         }
         
         // send out buffered data on blocking socket
         //
         mBufferStream.flip();
         while (mBufferStream.remaining() > 0) {
            mConnection.write(mBufferStream.getBuffer());
         }

      } catch (IOException e) {
         
         Log.d(TAG, e.toString());
         
      } catch (WebSocketException e) {

         Log.d(TAG, e.toString());
         
      } finally {
         
      }
   }
}
