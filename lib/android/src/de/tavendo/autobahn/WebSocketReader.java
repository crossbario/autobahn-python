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

import java.io.UnsupportedEncodingException;
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
   private final Handler mMaster;
   private final SocketChannel mSocket;
   
   private final static int STATE_CLOSED = 0;
   private final static int STATE_CONNECTING = 1;
   private final static int STATE_CLOSING = 2;
   private final static int STATE_OPEN = 3;
   
   private int mState;
   
   private NoCopyByteArrayOutputStream mData = new NoCopyByteArrayOutputStream();
   private NoCopyByteArrayOutputStream mHttpHeader = new NoCopyByteArrayOutputStream();
   
   private boolean mInsideMessage = false;
   
   private int mMessageOpcode;
   private NoCopyByteArrayOutputStream mMessagePayload = new NoCopyByteArrayOutputStream();
   
   /// Frame currently being received.
   private FrameHeader mCurrentFrame;
   
   /**
    * WebSockets frame metadata.
    */
   private static class FrameHeader {
      public int mOpcode;
      public boolean mFin;
      //public int mReserved;
      public int mHeaderLen;
      public long mPayloadLen;
      public long mTotalLen;
   }

   /**
    * Create new WebSockets background reader.
    * 
    * @param master    The message handler of master (foreground thread).
    * @param socket    The socket channel created on foreground thread.
    */
   public WebSocketReader(Handler master, SocketChannel socket) {

      super("WebSocketReader");
      
      mMaster = master;
      mSocket = socket;
      mBuffer = ByteBuffer.allocateDirect(BUFFER_SIZE);
      mCurrentFrame = null;
      
      mState = STATE_CONNECTING;
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
   
   private boolean processData() throws Exception {

      if (mCurrentFrame == null) {
         
         if (mData.size() >= 2) {
            
            byte[] da = mData.getByteArray();
            
            byte b0 = da[0];
            boolean fin = (b0 & 0x80) != 0;
            int rsv = (b0 & 0x70) >> 4;
            int opcode = b0 & 0x0f;
            
            byte b1 = da[1];
            boolean masked = (b1 & 0x80) != 0;
            int payload_len1 = b1 & 0x7f;
            
            // now check protocol compliance
            
            if (rsv != 0) {
               throw new WebSocketException("RSV != 0 and no extension negotiated");
            }
            
            if (masked) {
               // currently, we don't allow this. need to see whats the final spec.
               throw new WebSocketException("masked server frame");
            }
            
            if (opcode > 7) {
               // control frame
               if (!fin) {
                  throw new WebSocketException("fragmented control frame");
               }
               if (payload_len1 > 125) {
                  throw new WebSocketException("control frame with payload length > 125 octets");                    
               }
               if (opcode != 8 && opcode != 9 && opcode != 10) {
                  throw new WebSocketException("control frame using reserved opcode " + opcode);
               }
               if (opcode == 10 && payload_len1 == 1) {
                  throw new WebSocketException("received close control frame with payload len 1");
               }
            } else {
               // message frame
               if (opcode != 0 && opcode != 1 && opcode != 2) {
                  throw new WebSocketException("data frame using reserved opcode " + opcode);
               }
               if (!mInsideMessage && opcode == 0) {
                  throw new WebSocketException("received continuation data frame outside fragmented message");
               }
               if (mInsideMessage && opcode != 0) {
                  throw new WebSocketException("received non-continuation data frame while inside fragmented message");
               }
            }

            int mask_len = masked ? 4 : 0;
            int header_len = 0;
            
            if (payload_len1 < 126) {
               header_len = 2 + mask_len;
            } else if (payload_len1 == 126) {
               header_len = 2 + 2 + mask_len;
            } else if (payload_len1 == 127) {
               header_len = 2 + 8 + mask_len;
            } else {
               // should not arrive here
               throw new Exception("logic error");
            }
            
            if (mData.size() >= header_len) {
               
               int i = 2;
               long payload_len = 0;
               if (payload_len1 == 126) {
                  payload_len = ((0xff & da[i]) << 8) | (0xff & da[i+1]);
                  if (payload_len < 126) {
                     throw new WebSocketException("invalid data frame length (not using minimal length encoding)");
                  }
                  i += 2;
               } else if (payload_len1 == 127) {
                  if ((0x80 & da[i+0]) != 0) {
                     throw new WebSocketException("invalid data frame length (> 2^63)");
                  }
                  payload_len = ((0xff & da[i+0]) << 56) |
                                ((0xff & da[i+1]) << 48) |
                                ((0xff & da[i+2]) << 40) |
                                ((0xff & da[i+3]) << 32) |
                                ((0xff & da[i+4]) << 24) |
                                ((0xff & da[i+5]) << 16) |
                                ((0xff & da[i+6]) <<  8) |
                                ((0xff & da[i+7])      );
                  if (payload_len < 65536) {
                     throw new WebSocketException("invalid data frame length (not using minimal length encoding)");
                  }
                  i += 8;
               } else {
                  payload_len = payload_len1;
               }
               
               mCurrentFrame = new FrameHeader();
               mCurrentFrame.mOpcode = opcode;
               mCurrentFrame.mFin = fin;
               //mCurrentFrame.mReserved = rsv;
               mCurrentFrame.mPayloadLen = payload_len;
               mCurrentFrame.mHeaderLen = header_len;
               mCurrentFrame.mTotalLen = mCurrentFrame.mHeaderLen + mCurrentFrame.mPayloadLen;
               
               return mCurrentFrame.mPayloadLen == 0 || mData.size() >= mCurrentFrame.mTotalLen;
               
            } else {
               
               // need more data
               return false;
            }
         } else {
            
            // need more data
            return false;
         }

      } else {
         
         // within frame
         
         // see if we buffered complete frame
         if (mData.size() >= mCurrentFrame.mTotalLen) {
            
            // cut out frame payload
            byte[] framePayload = null;
            if (mCurrentFrame.mPayloadLen > 0) {
               framePayload = new byte[(int) mCurrentFrame.mPayloadLen];                     
               System.arraycopy(mData.getByteArray(), mCurrentFrame.mHeaderLen, framePayload, 0, (int) mCurrentFrame.mPayloadLen);
            }
            
            if (mCurrentFrame.mOpcode > 7) {
               // control frame
               
               if (mCurrentFrame.mOpcode == 8) {
                  // close
                  notify(new WebSocketMessage.Close());
                  
               } else if (mCurrentFrame.mOpcode == 9) {
                  // ping
                  notify(new WebSocketMessage.Ping(framePayload));
                  
               } else if (mCurrentFrame.mOpcode == 10) {
                  // pong
                  notify(new WebSocketMessage.Pong(framePayload));
                  
               } else {
                  
                  // illegal control frame
               }
               
            } else {
               // message frame
               
               if (!mInsideMessage) {
                  // new message started
                  mInsideMessage = true;
                  mMessageOpcode = mCurrentFrame.mOpcode;
               }
               
               if (framePayload != null) {
                  mMessagePayload.write(framePayload);
               }
               
               if (mCurrentFrame.mFin) {
                                    
                  if (mMessageOpcode == 1) {
                     
//                     String s = new String(mMessagePayload.getByteArray(), "UTF-8");                     
                     String s = new String(mMessagePayload.toByteArray(), "UTF-8");                     
                     notify(new WebSocketMessage.TextMessage(s));
                     
                  } else if (mMessageOpcode == 2) {
                                          
                     notify(new WebSocketMessage.BinaryMessage(mMessagePayload.toByteArray()));
                     
                  } else {
                     
                     // illegal data message
                  }
                  
                  mInsideMessage = false;
                  mMessagePayload.reset();
               }
            }      
            
            // rebuffer rest
            long restLen = mData.size() - mCurrentFrame.mTotalLen;
            if (restLen > 0) {
               byte[] rest = new byte[(int) restLen];
               System.arraycopy(mData.getByteArray(), mCurrentFrame.mHeaderLen + (int) mCurrentFrame.mPayloadLen, rest, 0, (int) restLen);
               mData.reset();
               mData.write(rest);
               mCurrentFrame = null;
               
               // process rest
               return true;
            } else {
               mData.reset();
               mCurrentFrame = null;
               
               // nothing more buffered
               return false;
            }
         } else {
            
            // need more data
            return false;
         }
      }
   }
   
   private void processHandshake() throws UnsupportedEncodingException {
      
      while (mBuffer.hasRemaining()) {
         
         // buffer HTTP headers in own stream
         mHttpHeader.write(mBuffer.get());

         // search end of HTTP header
         byte[] data = mHttpHeader.getByteArray();
         int pos = mHttpHeader.size() - 4;
         if (pos >= 0) {

            if (data[pos+0] == 0x0d &&
                data[pos+1] == 0x0a &&
                data[pos+2] == 0x0d &&
                data[pos+3] == 0x0a) {
               
               // FIXME: process handshake from server
               Log.d(TAG, mHttpHeader.toString("UTF-8"));

               // buffer rest
               while (mBuffer.hasRemaining()) {
                  mData.write(mBuffer.get());
               }
               mState = STATE_OPEN;
               break;
            }
         }
      }
      mBuffer.clear();
   }
   
   private void consumeData() throws Exception {
      
      if (mState == STATE_OPEN || mState == STATE_CLOSING) {
         
         // buffer rest
         while (mBuffer.hasRemaining()) {
            mData.write(mBuffer.get());
         }
         mBuffer.clear();
         
         while (processData()) {
            // reprocess until all buffered consumed or error occurred
         }
         
      } else if (mState == STATE_CONNECTING) {
         
         processHandshake();
      
      } else if (mState == STATE_CLOSED) {
      
      } else {
         // should not arrive here
      }
      
   }
   
   /**
    * Background reader thread loop.
    */
   @Override
   public void run() {

      try {
         
         mBuffer.clear();
         do {            
            // blocking read on socket
            while (true) {
               int len = mSocket.read(mBuffer);
               if (len > 0) {
                  mBuffer.flip();
                  break;
               }
            }
            // process buffered data            
            consumeData();
         } while (true);

      } catch (Exception e) {

         // wrap the exception and notify master
         notify(new WebSocketMessage.Error(e));
      }
   }

}
