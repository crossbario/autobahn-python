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
import java.util.concurrent.ConcurrentHashMap;

import org.codehaus.jackson.JsonFactory;
import org.codehaus.jackson.JsonParseException;
import org.codehaus.jackson.JsonParser;
import org.codehaus.jackson.JsonToken;
import org.codehaus.jackson.map.DeserializationConfig;
import org.codehaus.jackson.map.ObjectMapper;

import android.os.Handler;
import android.util.Log;
import de.tavendo.autobahn.AutobahnConnection.CallResultMeta;

public class AutobahnReader extends WebSocketReader {

   private static final String TAG = "de.tavendo.autobahn.AutobahnReader";

   private final ObjectMapper mJsonMapper;
   private final JsonFactory mJsonFactory;

   private final ConcurrentHashMap<String, CallResultMeta> mCalls;


   public AutobahnReader(ConcurrentHashMap<String, CallResultMeta> calls, Handler master, SocketChannel socket, WebSocketOptions options, String threadName) {

      super(master, socket, options, threadName);

      mCalls = calls;

      mJsonMapper = new ObjectMapper();
      mJsonMapper.configure(DeserializationConfig.Feature.FAIL_ON_UNKNOWN_PROPERTIES, false);
      mJsonFactory = mJsonMapper.getJsonFactory();
   }

   protected void onTextMessage(String payload) {

      // FIXME
      Log.d(TAG, "Error - received non-raw text message");
   }

   protected void onBinaryMessage(byte[] payload) {

      // FIXME
      Log.d(TAG, "Error - received binary message");
   }

   protected void onRawTextMessage(byte[] payload) {

      try {

         // create parser on top of raw UTF-8 payload
         JsonParser parser = mJsonFactory.createJsonParser(payload);

         // all Autobahn messages are JSON arrays
         if (parser.nextToken() == JsonToken.START_ARRAY) {

            // message type
            if (parser.nextToken() == JsonToken.VALUE_NUMBER_INT) {

               int msgType = parser.getIntValue();

               if (msgType == AutobahnMessage.MESSAGE_TYPE_CALL_RESULT) {

                  // call ID
                  parser.nextToken();
                  String callId = parser.getText();

                  // result
                  parser.nextToken();
                  Object result = null;

                  if (mCalls.containsKey(callId)) {

                     CallResultMeta meta = mCalls.get(callId);
                     if (meta.mResultClass != null) {
                        result = parser.readValueAs(meta.mResultClass);
                     } else if (meta.mResultTypeRef != null) {
                        result = parser.readValueAs(meta.mResultTypeRef);
                     } else {
                     }
                     notify(new AutobahnMessage.CallResult(callId, result));
                  }

               } else if (msgType == AutobahnMessage.MESSAGE_TYPE_CALL_ERROR) {

                  // call ID
                  parser.nextToken();
                  String callId = parser.getText();

                  // error URI
                  parser.nextToken();
                  String errorUri = parser.getText();

                  // error description
                  parser.nextToken();
                  String errorDesc = parser.getText();

                  if (mCalls.containsKey(callId)) {

                     notify(new AutobahnMessage.CallError(callId, errorUri, errorDesc));
                  }

               } else if (msgType == AutobahnMessage.MESSAGE_TYPE_EVENT) {

                  //parser.nextToken();
                  //String topicUri = parser.getText();

                  // FIXME: read object as ..

               } else if (msgType == AutobahnMessage.MESSAGE_TYPE_PREFIX) {

                  // prefix
                  parser.nextToken();
                  String prefix = parser.getText();

                  // URI
                  parser.nextToken();
                  String uri = parser.getText();

                  notify(new AutobahnMessage.Prefix(prefix, uri));

               } else {

                  // FIXME: invalid WAMP message

               }
            } else {
               // error: missing msg type
            }
            if (parser.nextToken() == JsonToken.END_ARRAY) {
            } else {
               // error: missing array close or invalid additional args
            }

         } else {
            // error: no array
         }
         parser.close();


      } catch (JsonParseException e) {
         e.printStackTrace();
      } catch (IOException e) {
         e.printStackTrace();
      }
   }
}
