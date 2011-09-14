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
import java.io.UnsupportedEncodingException;
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
   
   private void sendClose(int code, String reason) throws IOException {
      
      if (code > 0) {
         
         byte[] payload = null;
         
         if (reason != null && !reason.equals("")) {
            byte[] pReason = reason.getBytes("UTF-8");
            payload = new byte[2 + pReason.length];
            for (int i = 0; i < pReason.length; ++i) {
               payload[i + 2] = pReason[i];
            }            
         } else {
            payload = new byte[2];
         }

         payload[0] = (byte)((code >> 8) & 0xff);
         payload[1] = (byte)(code & 0xff);
         
         sendFrame(8, true, payload);
         
      } else {
         
         sendFrame(8, true, null);
      }
   }
   
   private void sendPing(byte[] payload) throws IOException {
      sendFrame(9, true, payload);
   }
   
   private void sendPong(byte[] payload) throws IOException {
      sendFrame(10, true, payload);
   }
   
   private void sendBinaryMessage(byte[] payload) throws IOException {      
      sendFrame(2, true, payload);
   }
   
   private void sendTextMessage(String payload) throws UnsupportedEncodingException, IOException {      
      sendFrame(1, true, payload.getBytes("UTF-8"));
   }
   
   private void sendFrame(int opcode, boolean fin, byte[] payload) throws IOException {
      
      // first octet
      //
      byte b0 = 0;
      if (fin) {
         b0 |= (byte) (1 << 7);
      }      
      b0 |= (byte) opcode;
      mBufferStream.write(b0);
      
      // second octet
      byte b1 = (byte) (1 << 7); // c2s is always masked

      long len = 0;
      if (payload != null) {
         len = payload.length;
      }
      
      if (len < 125) {
         b1 |= (byte) len;
         mBufferStream.write(b1);
      } else if (len <= 0xffff) {
         b1 |= (byte) 126;
         mBufferStream.write(b1);
         mBufferStream.write(new byte[] {(byte)((len >> 8) & 0xff),
                                         (byte)(len & 0xff)});         
      } else {
         b1 |= (byte) 127;
         mBufferStream.write(b1);
         mBufferStream.write(new byte[] {(byte)((len >> 56) & 0xff),
                                         (byte)((len >> 48) & 0xff),
                                         (byte)((len >> 40) & 0xff),
                                         (byte)((len >> 32) & 0xff),
                                         (byte)((len >> 24) & 0xff),
                                         (byte)((len >> 16) & 0xff),
                                         (byte)((len >> 8)  & 0xff),
                                         (byte)(len         & 0xff)});         
      }
      
      mBufferStream.write(0);
      mBufferStream.write(0);
      mBufferStream.write(0);
      mBufferStream.write(0);
      
      if (len > 0) {
         for (int i = 0; i < len; ++i) {
            payload[i] ^= 0;
         }      
         mBufferStream.write(payload);         
      }
   }

   @Override
   public void handleMessage(Message msg) {

      try {

         mBufferStream.clear();

         if (msg.obj instanceof WebSocketMessage.TextMessage) {
            
            WebSocketMessage.TextMessage textMessage = (WebSocketMessage.TextMessage) msg.obj;
            sendTextMessage(textMessage.mPayload);
            
         } else if (msg.obj instanceof WebSocketMessage.BinaryMessage) {
            
            WebSocketMessage.BinaryMessage binaryMessage = (WebSocketMessage.BinaryMessage) msg.obj;
            sendBinaryMessage(binaryMessage.mPayload);
            
         } else if (msg.obj instanceof WebSocketMessage.Ping) {
            
            WebSocketMessage.Ping pingMessage = (WebSocketMessage.Ping) msg.obj;
            sendPing(pingMessage.mPayload);
            
         } else if (msg.obj instanceof WebSocketMessage.Pong) {
            
            WebSocketMessage.Pong pongMessage = (WebSocketMessage.Pong) msg.obj;
            sendPong(pongMessage.mPayload);
            
         } else if (msg.obj instanceof WebSocketMessage.Close) {
            
            WebSocketMessage.Close closeMessage = (WebSocketMessage.Close) msg.obj;
            sendClose(closeMessage.mCode, closeMessage.mReason);
            
         } else if (msg.obj instanceof WebSocketMessage.ClientHandshake) {
            
            WebSocketMessage.ClientHandshake clientHandshakeMessage = (WebSocketMessage.ClientHandshake) msg.obj;
            
            mBufferStream.write("GET " + clientHandshakeMessage.mPath + " HTTP/1.1");
            mBufferStream.crlf();
            mBufferStream.write("Host: " + clientHandshakeMessage.mHost);
            mBufferStream.crlf();
            mBufferStream.write("Upgrade: WebSocket");
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
