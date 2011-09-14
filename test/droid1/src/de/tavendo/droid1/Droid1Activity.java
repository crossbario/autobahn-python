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

package de.tavendo.droid1;

import de.tavendo.autobahn.WebSocketConnection;
import de.tavendo.autobahn.WebSocketException;
import android.app.Activity;
import android.os.Bundle;
import android.util.Log;

public class Droid1Activity extends Activity {

   static final String TAG = "AUTOBAHN";

   @Override
   public void onCreate(Bundle savedInstanceState) {
      super.onCreate(savedInstanceState);
      setContentView(R.layout.main);
      
      WebSocketConnection sess = new WebSocketConnection();
      try {
         sess.connect("ws://192.168.1.130:9000");
         sess.send("Hallo, Arsch!!");
         sess.send("A second message.");
         sess.send("My last word!");
      } catch (WebSocketException e) {
         
         Log.d(TAG, e.toString());
      }

      /*
      AutobahnException e = new AutobahnException("protocol violation");
      Log.d(TAG, e.toString());

      Log.d(TAG, "Main.onCreate on Thread " + Thread.currentThread().getId());
      
      Autobahn service = new AutobahnConnection();

      service.call("getUser", Integer.class, new Autobahn.OnCallResult() {
         @Override
         public void onResult(Object result) {
            Log.d(TAG, "RPC Result = " + result.toString());
         }

         @Override
         public void onError(String errorId, String errorInfo) {
         }
      }, 666);
*/      
   }
      
}