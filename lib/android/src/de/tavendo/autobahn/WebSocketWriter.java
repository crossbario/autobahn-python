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
import java.util.Random;

/**
 * WebSocket Writer. This is run on own background thread with own message loop.
 * The only method that needs to be called (from foreground thread) is forward(),
 * which is used to forward a WebSockets message to this object (running on
 * background thread) so that it can be formatted and sent out on socket.
 */
public class WebSocketWriter extends Handler {
   
   @SuppressWarnings("unused")
   private static final String TAG = "de.tavendo.autobahn.WebSocketWriter";

   /// Random number generator for handshake key and frame mask generation.
   private final Random mRng = new Random();
   
   private final Handler mMaster;

   /// The NIO socket channel created on foreground thread.
   private final SocketChannel mSocket;
   
   /// The send buffer that holds data to send on socket.
   private final ByteBufferOutputStream mBuffer;

   /**
    * Create new WebSockets background writer.
    * 
    * @param looper    The message looper of the background thread on which
    *                  this object is running.
    * @param master    The message handler of master (foreground thread).
    * @param socket    The socket channel created on foreground thread.
    */
   public WebSocketWriter(Looper looper, Handler master, SocketChannel socket) {

      super(looper);
      
      mMaster = master;
      mSocket = socket;
      mBuffer = new ByteBufferOutputStream();
   }
   
   /**
    * This can be called on foreground thread to send this object
    * (running on background thread) a WebSocket message to send.
    * 
    * @param message       Message to send to WebSockets writer.
    */
   public void forward(WebSocketMessage.Message message) {
      
      Message msg = obtainMessage();
      msg.obj = message;
      sendMessage(msg);
   }
   
   /**
    * Notify the master (foreground thread).
    * 
    * @param message       Message to send to master.       
    */
   private void notify(WebSocketMessage.Message message) {
      
      Message msg = mMaster.obtainMessage();
      msg.obj = message;
      mMaster.sendMessage(msg);      
   }
   
   /**
    * Create new key for WebSockets handshake.
    * 
    * @return WebSockets handshake key (Base64 encoded).
    */
   private String newHandshakeKey() {
      final byte[] ba = new byte[16];
      mRng.nextBytes(ba);
      return Base64.encodeToString(ba, Base64.DEFAULT);
   }
   
   /**
    * Create new (random) frame mask.
    * 
    * @return Frame mask (4 octets).
    */
   private byte[] newFrameMask() {
      final byte[] ba = new byte[4];
      mRng.nextBytes(ba);
      return ba;
   }
   
   /**
    * Send WebSocket client handshake.
    */
   private void sendClientHandshake(WebSocketMessage.ClientHandshake message) throws IOException {
      
      // write HTTP header with handshake
      mBuffer.write("GET " + message.mPath + " HTTP/1.1");
      mBuffer.crlf();
      mBuffer.write("Host: " + message.mHost);
      mBuffer.crlf();
      mBuffer.write("Upgrade: WebSocket");
      mBuffer.crlf();
      mBuffer.write("Connection: Upgrade");
      mBuffer.crlf();
      mBuffer.write("Sec-WebSocket-Key: " + newHandshakeKey());
      mBuffer.crlf();
      if (message.mOrigin != null && !message.mOrigin.equals("")) {
         mBuffer.write("Origin: " + message.mOrigin);
         mBuffer.crlf();
      }
      mBuffer.write("Sec-WebSocket-Version: 13");
      mBuffer.crlf();
      mBuffer.crlf();      
   }

   /**
    * Send WebSockets close.
    */
   private void sendClose(WebSocketMessage.Close message) throws IOException {
      
      if (message.mCode > 0) {
         
         byte[] payload = null;
         
         if (message.mReason != null && !message.mReason.equals("")) {
            byte[] pReason = message.mReason.getBytes("UTF-8");
            payload = new byte[2 + pReason.length];
            for (int i = 0; i < pReason.length; ++i) {
               payload[i + 2] = pReason[i];
            }            
         } else {
            payload = new byte[2];
         }

         payload[0] = (byte)((message.mCode >> 8) & 0xff);
         payload[1] = (byte)(message.mCode & 0xff);
         
         sendFrame(8, true, payload);
         
      } else {
         
         sendFrame(8, true, null);
      }
   }
   
   /**
    * Send WebSockets ping.
    */
   private void sendPing(WebSocketMessage.Ping message) throws IOException {
      sendFrame(9, true, message.mPayload);
   }
   
   /**
    * Send WebSockets pong. Normally, unsolicited Pongs are not used,
    * but Pongs are only send in response to a Ping from the peer.
    */
   private void sendPong(WebSocketMessage.Pong message) throws IOException {
      sendFrame(10, true, message.mPayload);
   }
   
   /**
    * Send WebSockets binary message.
    */
   private void sendBinaryMessage(WebSocketMessage.BinaryMessage message) throws IOException {      
      sendFrame(2, true, message.mPayload);
   }
   
   /**
    * Send WebSockets text message.
    */
   private void sendTextMessage(WebSocketMessage.TextMessage message) throws IOException {      
      sendFrame(1, true, message.mPayload.getBytes("UTF-8"));
   }
   
   /**
    * Send WebSockets frame.
    * 
    * @param opcode           Frame opcode.
    * @param fin              Final frame flag.
    * @param payload          Frame payload.
    */
   private void sendFrame(int opcode, boolean fin, byte[] payload) throws IOException {
      
      // first octet
      byte b0 = 0;
      if (fin) {
         b0 |= (byte) (1 << 7);
      }      
      b0 |= (byte) opcode;
      mBuffer.write(b0);
      
      // second octet
      byte b1 = (byte) (1 << 7); // c2s is always masked

      long len = 0;
      if (payload != null) {
         len = payload.length;
      }
      
      // extended payload length
      if (len < 125) {
         b1 |= (byte) len;
         mBuffer.write(b1);
      } else if (len <= 0xffff) {
         b1 |= (byte) 126;
         mBuffer.write(b1);
         mBuffer.write(new byte[] {(byte)((len >> 8) & 0xff),
                                         (byte)(len & 0xff)});         
      } else {
         b1 |= (byte) 127;
         mBuffer.write(b1);
         mBuffer.write(new byte[] {(byte)((len >> 56) & 0xff),
                                         (byte)((len >> 48) & 0xff),
                                         (byte)((len >> 40) & 0xff),
                                         (byte)((len >> 32) & 0xff),
                                         (byte)((len >> 24) & 0xff),
                                         (byte)((len >> 16) & 0xff),
                                         (byte)((len >> 8)  & 0xff),
                                         (byte)(len         & 0xff)});         
      }
      
      // a mask is always needed, even without payload
      byte mask[] = newFrameMask();      
      mBuffer.write(mask[0]);
      mBuffer.write(mask[1]);
      mBuffer.write(mask[2]);
      mBuffer.write(mask[3]);
      
      if (len > 0) {
         // FIXME: optimize
         // FIXME: masking within buffer of output stream
         for (int i = 0; i < len; ++i) {
            payload[i] ^= mask[i % 4];
         }      
         mBuffer.write(payload);         
      }
   }

   /**
    * Process message received from foreground thread. This is called from
    * the message looper.
    */
   @Override
   public void handleMessage(Message msg) {

      try {
         
         // clear send buffer
         mBuffer.clear();

         // 
         if (msg.obj instanceof WebSocketMessage.TextMessage) {
            
            sendTextMessage((WebSocketMessage.TextMessage) msg.obj);
            
         } else if (msg.obj instanceof WebSocketMessage.BinaryMessage) {
            
            sendBinaryMessage((WebSocketMessage.BinaryMessage) msg.obj);
            
         } else if (msg.obj instanceof WebSocketMessage.Ping) {
            
            sendPing((WebSocketMessage.Ping) msg.obj);
            
         } else if (msg.obj instanceof WebSocketMessage.Pong) {
            
            sendPong((WebSocketMessage.Pong) msg.obj);
            
         } else if (msg.obj instanceof WebSocketMessage.Close) {
            
            sendClose((WebSocketMessage.Close) msg.obj);
            
         } else if (msg.obj instanceof WebSocketMessage.ClientHandshake) {
            
            sendClientHandshake((WebSocketMessage.ClientHandshake) msg.obj);
                        
         } else {
            
            // should never arrive here
            throw new WebSocketException("invalid message to WebSocketWriter");
            
         }
         
         // send out buffered data
         //
         mBuffer.flip();
         while (mBuffer.remaining() > 0) {
            // this can block on socket write
            mSocket.write(mBuffer.getBuffer());
         }

      } catch (Exception e) {
         
         // wrap the exception and notify master
         notify(new WebSocketMessage.Error(e));
      }
   }
}
