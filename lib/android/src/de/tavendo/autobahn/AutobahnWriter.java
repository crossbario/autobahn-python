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

import org.codehaus.jackson.JsonFactory;
import org.codehaus.jackson.JsonGenerationException;
import org.codehaus.jackson.JsonGenerator;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.MappingJsonFactory;

import android.os.Handler;
import android.os.Looper;

public class AutobahnWriter extends WebSocketWriter {

   private static final int MESSAGE_TYPE_CALL = 1;

   private final JsonFactory mJsonFactory;
   private final NoCopyByteArrayOutputStream mPayload;

   public AutobahnWriter(Looper looper, Handler master, SocketChannel socket,
         WebSocketOptions options) {
      super(looper, master, socket, options);
      mJsonFactory = new MappingJsonFactory();
      mPayload = new NoCopyByteArrayOutputStream();
   }

   protected void processAppMessage(Object msg) throws WebSocketException, IOException {

      mPayload.reset();
      JsonGenerator generator = mJsonFactory.createJsonGenerator(mPayload);

      try {

         if (msg instanceof AutobahnMessage.Call) {

            AutobahnMessage.Call call = (AutobahnMessage.Call) msg;

            generator.writeStartArray();
            generator.writeNumber(MESSAGE_TYPE_CALL);
            generator.writeString(call.callId);
            generator.writeString(call.procUri);
            generator.writeObject(call.args);
            generator.writeEndArray();

         } else {

            throw new WebSocketException("unknown message received by AutobahnWriter");
         }
      } catch (JsonGenerationException e) {

      } catch (JsonMappingException e) {

      }

      generator.flush();
      sendFrame(1, true, mPayload.getByteArray(), 0, mPayload.size());
      generator.close();

   }
}
