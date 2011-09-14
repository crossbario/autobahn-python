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

   private static final int BUFFER_SIZE = 4096;
   private final ByteBuffer mBuffer;
   private final Handler mHandler;
   private final SocketChannel mConnection;
   
   private final static int STATE_CLOSED = 0;
   private final static int STATE_CONNECTING = 1;
   private final static int STATE_CLOSING = 2;
   private final static int STATE_OPEN = 3;
   
   private int mState;

   public WebSocketReader(Handler handler, SocketChannel connection) {

      super("WebSocketReader");
      
      mHandler = handler;
      mConnection = connection;
      mBuffer = ByteBuffer.allocateDirect(BUFFER_SIZE);
      
      mState = STATE_CONNECTING;
   }

   @Override
   public void run() {

      Log.d(TAG, "TransportReader::run()");
      try {
         ByteArrayOutputStream baos = new ByteArrayOutputStream();
         do {

            mBuffer.clear();
            int len = mConnection.read(mBuffer);

            if (len < 0)
               break;

            Log.d(TAG, "ok, READ " + len + " bytes");
            
            // WebSocket needs handshake
            if (mState == STATE_CONNECTING) {
               
               // search end of HTTP header
               for (int i = len - 4; i >= 0; --i) {
                  if (mBuffer.get(i+0) == 0x0d &&
                      mBuffer.get(i+1) == 0x0a &&
                      mBuffer.get(i+2) == 0x0d &&
                      mBuffer.get(i+3) == 0x0a) {
                     
                     for (int j = 0; j <= i+3; ++j) {
                        baos.write(mBuffer.get(j));
                     }
                     
                     Log.d(TAG, baos.toString("UTF-8"));
                     
                     baos.reset();
                     
                     for (int j = i+4; j < len; ++j) {
                        baos.write(mBuffer.get(j));
                     }
                     
                     mState = STATE_OPEN;
                     break;
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
