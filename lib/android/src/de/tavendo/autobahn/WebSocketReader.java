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

import java.io.ByteArrayOutputStream;
import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;

import android.os.Handler;
import android.os.Message;
import android.util.Log;

/**
 * Transport Reader. This is run on own background thread and posts messages
 * to main thread.
 */
public class WebSocketReader extends Thread {

   private static final String TAG = "de.tavendo.autobahn.WebSocketReader";

   // private final ObjectMapper mJsonMapper = new ObjectMapper();
   // private final JsonFactory mJsonFactory;

   private static final int BUFFER_SIZE = 65536;
   private final ByteBuffer mBuffer;
   private final Handler mHandler;
   private final SocketChannel mConnection;
   
   private final static int STATE_CLOSED = 0;
   private final static int STATE_CONNECTING = 1;
   private final static int STATE_CLOSING = 2;
   private final static int STATE_OPEN = 3;
   
   private int mState;
   
   private FrameHeader mCurrentFrame;
   
   private static class FrameHeader {
      public int mOpcode;
      public boolean mFin;
      public int mHeaderLen;
      public long mPayloadLen;
   }

   public WebSocketReader(Handler handler, SocketChannel connection) {

      super("WebSocketReader");
      
      mHandler = handler;
      mConnection = connection;
      mBuffer = ByteBuffer.allocateDirect(BUFFER_SIZE);
      mCurrentFrame = null;
      
      mState = STATE_CONNECTING;
   }

   @Override
   public void run() {

      Log.d(TAG, "TransportReader::run()");
      try {
         
         NoCopyByteArrayOutputStream data = new NoCopyByteArrayOutputStream();
         boolean reprocess = false;
         int len = 0;
         
         do {
            
            if (!reprocess) {

               // blocking read on socket
               while (true) {
                  len = mConnection.read(mBuffer);
                  if (len > 0) break;
               }
   
               Log.d(TAG, "ok, READ " + len + " bytes");
            }
            
            // WebSocket needs handshake
            if (mState == STATE_CONNECTING) {
               
               // search end of HTTP header
               for (int i = len - 4; i >= 0; --i) {
                  if (mBuffer.get(i+0) == 0x0d &&
                      mBuffer.get(i+1) == 0x0a &&
                      mBuffer.get(i+2) == 0x0d &&
                      mBuffer.get(i+3) == 0x0a) {
                     
                     for (int j = 0; j <= i + 3; ++j) {
                        data.write(mBuffer.get(j));
                     }
                     
                     // FIXME: process handshake from server
                     Log.d(TAG, data.toString("UTF-8"));
                     
                     data.reset();
                     
                     // buffer rest after HTTP header if any
                     for (int j = i + 4; j < len; ++j) {
                        data.write(mBuffer.get(j));
                     }
                     
                     mBuffer.clear();
                     len = 0;
                     
                     mState = STATE_OPEN;
                     break;
                  }
               }               
            } else {
               
               // buffer to byte array stream
               for (int i = 0; i < len; ++i) {
                  data.write(mBuffer.get(i));
               }

               mBuffer.clear();
               len = 0;
            }
            
            if (mState == STATE_OPEN) {
               
               Log.d(TAG, "SIZE = " + data.size());
               Log.d(TAG, "LENGTH = " + data.getByteArray().length);
               
               if (mCurrentFrame == null) {
                  
                  if (data.size() >= 2) {
                     
                     byte[] da = data.getByteArray();
                     
                     byte b0 = da[0];
                     boolean fin = (b0 & 0x80) != 0;
                     int rsv = (b0 & 0x70) >> 4;
                     int opcode = b0 & 0x0f;

                     byte b1 = da[1];
                     boolean masked = (b1 & 0x80) != 0;
                     int payload_len1 = b1 & 0x7f;
                     
                     int mask_len = masked ? 4 : 0;
                     int header_len = 0;
                     
                     if (payload_len1 < 126) {
                        header_len = 2 + mask_len;
                     } else if (payload_len1 == 126) {
                        header_len = 2 + 2 + mask_len;
                     } else if (payload_len1 == 127) {
                        header_len = 2 + 8 + mask_len;
                     } else {
                        
                     }
                     
                     if (data.size() >= header_len) {
                        
                        int i = 2;
                        long payload_len = 0;
                        if (payload_len1 == 126) {
                           payload_len = ((0xff & da[i]) << 8) | (0xff & da[i+1]);
                           i += 2;
                        } else if (payload_len1 == 127) {
                           payload_len = ((0xff & da[i+0]) << 56) |
                                         ((0xff & da[i+1]) << 48) |
                                         ((0xff & da[i+2]) << 40) |
                                         ((0xff & da[i+3]) << 32) |
                                         ((0xff & da[i+4]) << 24) |
                                         ((0xff & da[i+5]) << 16) |
                                         ((0xff & da[i+6]) <<  8) |
                                         ((0xff & da[i+7])      );
                           i += 8;
                        } else {
                           payload_len = payload_len1;
                        }
                        
                        mCurrentFrame = new FrameHeader();
                        mCurrentFrame.mOpcode = opcode;
                        mCurrentFrame.mFin = fin;
                        mCurrentFrame.mPayloadLen = payload_len;
                        mCurrentFrame.mHeaderLen = header_len;
                     }
                  }

               }
               
               if (mCurrentFrame != null) {
                  long totalLen = mCurrentFrame.mHeaderLen + mCurrentFrame.mPayloadLen;
                  if (data.size() >= totalLen) {
                     
                     Log.d(TAG, "Payload Length = " + mCurrentFrame.mPayloadLen);
                     
                     byte[] pl = new byte[(int) mCurrentFrame.mPayloadLen];
                     
                     System.arraycopy(data.getByteArray(), mCurrentFrame.mHeaderLen, pl, 0, (int) mCurrentFrame.mPayloadLen);
                     
                     String s = new String(pl, "UTF-8");
                     
                     Log.d(TAG, "XXX = " + s);
                     
                     long restLen = data.size() - totalLen;

                     if (restLen > 0) {
                        byte[] rest = new byte[(int) restLen];
                        System.arraycopy(data.getByteArray(), mCurrentFrame.mHeaderLen + (int) mCurrentFrame.mPayloadLen, rest, 0, (int) restLen);
                        data.reset();
                        data.write(rest);
                        reprocess = true;
                     } else {
                        data.reset();
                        reprocess = false;
                     }

                     Log.d(TAG, "restLen : " + restLen);
                     Log.d(TAG, "buffered length after frame processed : " + data.size());
                     
                     mCurrentFrame = null;
                  }                  
               }
                              
            } else {
               
            }
/*
            for (int i = 0; i < len; ++i) {
               byte b = mBuffer.get(i);
               if (b == 0) {
                  Object obj = baos.toByteArray();
                  baos = new ByteArrayOutputStream();
                  Message msg = mHandler.obtainMessage();
                  msg.obj = obj;
                  mHandler.sendMessage(msg);
               } else {
                  baos.write(b);
               }
            }
*/            
         } while (true);
      } catch (Exception e) {
         // TODO Auto-generated catch block
         e.printStackTrace();
         Log.d(TAG, "SHIT : " + e.toString());
      }
   }

}
