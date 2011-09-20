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

/**
 * Transport Reader. This is run on own background thread and posts messages
 * to main thread.
 */
public class WebSocketReader extends Thread {

   @SuppressWarnings("unused")
   private static final String TAG = "de.tavendo.autobahn.WebSocketReader";

   private final Handler mMaster;
   private final SocketChannel mSocket;
   private final WebSocketOptions mOptions;

   private final ByteBuffer mFrameBuffer;
   private NoCopyByteArrayOutputStream mMessagePayload;

   private final static int STATE_CLOSED = 0;
   private final static int STATE_CONNECTING = 1;
   private final static int STATE_CLOSING = 2;
   private final static int STATE_OPEN = 3;

   private boolean mStopped = false;
   private int mState;

   private boolean mInsideMessage = false;
   private int mMessageOpcode;

   /// Frame currently being received.
   private FrameHeader mFrameHeader;

   private Utf8Validator mUtf8Validator = new Utf8Validator();


   /**
    * WebSockets frame metadata.
    */
   private static class FrameHeader {
      public int mOpcode;
      public boolean mFin;
      @SuppressWarnings("unused")
      public int mReserved;
      public int mHeaderLen;
      public int mPayloadLen;
      public int mTotalLen;
      public byte[] mMask;
   }


   /**
    * Create new WebSockets background reader.
    *
    * @param master    The message handler of master (foreground thread).
    * @param socket    The socket channel created on foreground thread.
    */
   public WebSocketReader(Handler master, SocketChannel socket, WebSocketOptions options, String threadName) {

      super(threadName);

      mMaster = master;
      mSocket = socket;
      mOptions = options;

      mFrameBuffer = ByteBuffer.allocateDirect(options.getMaxFramePayloadSize() + 14);
      mMessagePayload = new NoCopyByteArrayOutputStream(options.getMaxMessagePayloadSize());

      mFrameHeader = null;
      mState = STATE_CONNECTING;
   }


   /**
    * Graceful shutdown of background writer (called from master).
    */
   public void quit() {
      mStopped = true;
   }


   /**
    * Notify the master (foreground thread).
    *
    * @param message       Message to send to master.
    */
   protected void notify(Object message) {

      Message msg = mMaster.obtainMessage();
      msg.obj = message;
      mMaster.sendMessage(msg);
   }


   /**
    * Process incoming WebSockets data (after handshake).
    */
   private boolean processData() throws Exception {

      // outside frame?
      if (mFrameHeader == null) {

         // need at least 2 bytes from WS frame header to start processing
         if (mFrameBuffer.position() >= 2) {

            byte b0 = mFrameBuffer.get(0);
            boolean fin = (b0 & 0x80) != 0;
            int rsv = (b0 & 0x70) >> 4;
            int opcode = b0 & 0x0f;

            byte b1 = mFrameBuffer.get(1);
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

            // continue when complete frame header is available
            if (mFrameBuffer.position() >= header_len) {

               // determine frame payload length
               int i = 2;
               long payload_len = 0;
               if (payload_len1 == 126) {
                  payload_len = ((0xff & mFrameBuffer.get(i)) << 8) | (0xff & mFrameBuffer.get(i+1));
                  if (payload_len < 126) {
                     throw new WebSocketException("invalid data frame length (not using minimal length encoding)");
                  }
                  i += 2;
               } else if (payload_len1 == 127) {
                  if ((0x80 & mFrameBuffer.get(i+0)) != 0) {
                     throw new WebSocketException("invalid data frame length (> 2^63)");
                  }
                  payload_len = ((0xff & mFrameBuffer.get(i+0)) << 56) |
                                ((0xff & mFrameBuffer.get(i+1)) << 48) |
                                ((0xff & mFrameBuffer.get(i+2)) << 40) |
                                ((0xff & mFrameBuffer.get(i+3)) << 32) |
                                ((0xff & mFrameBuffer.get(i+4)) << 24) |
                                ((0xff & mFrameBuffer.get(i+5)) << 16) |
                                ((0xff & mFrameBuffer.get(i+6)) <<  8) |
                                ((0xff & mFrameBuffer.get(i+7))      );
                  if (payload_len < 65536) {
                     throw new WebSocketException("invalid data frame length (not using minimal length encoding)");
                  }
                  i += 8;
               } else {
                  payload_len = payload_len1;
               }

               // immediately bail out on frame too large
               if (payload_len > mOptions.getMaxFramePayloadSize()) {
                  throw new WebSocketException("frame payload too large");
               }

               // save frame header metadata
               mFrameHeader = new FrameHeader();
               mFrameHeader.mOpcode = opcode;
               mFrameHeader.mFin = fin;
               mFrameHeader.mReserved = rsv;
               mFrameHeader.mPayloadLen = (int) payload_len;
               mFrameHeader.mHeaderLen = header_len;
               mFrameHeader.mTotalLen = mFrameHeader.mHeaderLen + mFrameHeader.mPayloadLen;
               if (masked) {
                  mFrameHeader.mMask = new byte[4];
                  for (int j = 0; j < 4; ++j) {
                     mFrameHeader.mMask[i] = (byte) (0xff & mFrameBuffer.get(i + j));
                  }
                  i += 4;
               } else {
                  mFrameHeader.mMask = null;
               }

               // continue processing when payload empty or completely buffered
               return mFrameHeader.mPayloadLen == 0 || mFrameBuffer.position() >= mFrameHeader.mTotalLen;

            } else {

               // need more data
               return false;
            }
         } else {

            // need more data
            return false;
         }

      } else {

         // FIXME: refactor this for streaming processing, incl. fail fast
         // on invalid UTF-8 within frame already

         // within frame

         // see if we buffered complete frame
         if (mFrameBuffer.position() >= mFrameHeader.mTotalLen) {

            // cut out frame payload
            byte[] framePayload = null;
            int oldPosition = mFrameBuffer.position();
            if (mFrameHeader.mPayloadLen > 0) {
               framePayload = new byte[mFrameHeader.mPayloadLen];
               mFrameBuffer.position(mFrameHeader.mHeaderLen);
               mFrameBuffer.get(framePayload, 0, (int) mFrameHeader.mPayloadLen);
            }
            mFrameBuffer.position(mFrameHeader.mTotalLen);
            mFrameBuffer.limit(oldPosition);
            mFrameBuffer.compact();

            if (mFrameHeader.mOpcode > 7) {
               // control frame

               if (mFrameHeader.mOpcode == 8) {
                  // dispatch WS close
                  // FIXME: parse close payload
                  onClose();

               } else if (mFrameHeader.mOpcode == 9) {
                  // dispatch WS ping
                  onPing(framePayload);

               } else if (mFrameHeader.mOpcode == 10) {
                  // dispatch WS pong
                  onPong(framePayload);

               } else {

                  // should not arrive here (handled before)
                  throw new Exception("logic error");
               }

            } else {
               // message frame

               if (!mInsideMessage) {
                  // new message started
                  mInsideMessage = true;
                  mMessageOpcode = mFrameHeader.mOpcode;
                  if (mMessageOpcode == 1 && mOptions.getValidateIncomingUtf8()) {
                     mUtf8Validator.reset();
                  }
               }

               if (framePayload != null) {

                  // immediately bail out on message too large
                  if (mMessagePayload.size() + framePayload.length > mOptions.getMaxMessagePayloadSize()) {
                     throw new WebSocketException("message payload too large");
                  }

                  // validate incoming UTF-8
                  if (mMessageOpcode == 1 && mOptions.getValidateIncomingUtf8() && !mUtf8Validator.validate(framePayload)) {
                     throw new WebSocketException("invalid UTF-8 in text message payload");
                  }

                  // buffer frame payload for message
                  mMessagePayload.write(framePayload);
               }

               // on final frame ..
               if (mFrameHeader.mFin) {

                  if (mMessageOpcode == 1) {

                     // verify that UTF-8 ends on codepoint
                     if (mOptions.getValidateIncomingUtf8() && !mUtf8Validator.isValid()) {
                        throw new WebSocketException("UTF-8 text message payload ended within Unicode code point");
                     }

                     // deliver text message
                     if (mOptions.getReceiveTextMessagesRaw()) {

                        // dispatch WS text message as raw (but validated) UTF-8
                        onRawTextMessage(mMessagePayload.toByteArray());

                     } else {

                        // dispatch WS text message as Java String (previously already validated)
                        String s = new String(mMessagePayload.toByteArray(), "UTF-8");
                        onTextMessage(s);
                     }

                  } else if (mMessageOpcode == 2) {

                     // dispatch WS binary message
                     onBinaryMessage(mMessagePayload.toByteArray());

                  } else {

                     // should not arrive here (handled before)
                     throw new Exception("logic error");
                  }

                  // ok, message completed - reset all
                  mInsideMessage = false;
                  mMessagePayload.reset();
               }
            }

            // reset frame
            mFrameHeader = null;

            // reprocess if more data left
            return mFrameBuffer.position() > 0;

         } else {

            // need more data
            return false;
         }
      }
   }


   /**
    * WS close received. Default notifies master.
    */
   protected void onClose() {

      notify(new WebSocketMessage.Close());
   }


   /**
    * WS ping received. Default notifies master.
    */
   protected void onPing(byte[] payload) {

      notify(new WebSocketMessage.Ping(payload));
   }


   /**
    * WS pong received. Default notifies master.
    */
   protected void onPong(byte[] payload) {

      notify(new WebSocketMessage.Pong(payload));
   }


   /**
    * WS text message received. Default notifies master.
    */
   protected void onTextMessage(String payload) {

      notify(new WebSocketMessage.TextMessage(payload));
   }


   /**
    * WS text message received. Default notifies master.
    */
   protected void onRawTextMessage(byte[] payload) {

      notify(new WebSocketMessage.RawTextMessage(payload));
   }


   /**
    * WS binary message received. Default notifies master.
    */
   protected void onBinaryMessage(byte[] payload) {

      notify(new WebSocketMessage.BinaryMessage(payload));
   }


   /**
    * Process WS handshake received from server.
    */
   private boolean processHandshake() throws UnsupportedEncodingException {

      boolean res = false;
      for (int pos = mFrameBuffer.position() - 4; pos >= 0; --pos) {
         if (mFrameBuffer.get(pos+0) == 0x0d &&
             mFrameBuffer.get(pos+1) == 0x0a &&
             mFrameBuffer.get(pos+2) == 0x0d &&
             mFrameBuffer.get(pos+3) == 0x0a) {

            // FIXME: process & verify handshake from server

            notify(new WebSocketMessage.ServerHandshake());

            int oldPosition = mFrameBuffer.position();
            mFrameBuffer.position(pos + 4);
            mFrameBuffer.limit(oldPosition);
            mFrameBuffer.compact();

            // process further when data after HTTP headers left in buffer
            res = mFrameBuffer.position() > 0;

            mState = STATE_OPEN;
            break;
         }
      }
      return res;
   }


   /**
    * Consume data buffered in mFrameBuffer.
    */
   private boolean consumeData() throws Exception {

      if (mState == STATE_OPEN || mState == STATE_CLOSING) {

         return processData();

      } else if (mState == STATE_CONNECTING) {

         return processHandshake();

      } else if (mState == STATE_CLOSED) {

         return false;

      } else {
         // should not arrive here
         return false;
      }

   }


   /**
    * Background reader thread loop.
    */
   @Override
   public void run() {

      try {

         mFrameBuffer.clear();
         do {
            // blocking read on socket
            int len = mSocket.read(mFrameBuffer);
            if (len > 0) {
               // process buffered data
               while (consumeData()) {
               }
            } else if (len < 0) {
               notify(new WebSocketMessage.ConnectionLost());
               mStopped = true;
            }
         } while (!mStopped);

      } catch (WebSocketException e) {

         // wrap the exception and notify master
         notify(new WebSocketMessage.ProtocolViolation(e));

      } catch (Exception e) {

         // wrap the exception and notify master
         notify(new WebSocketMessage.Error(e));

      } finally {

         mStopped = true;
      }
   }

}
