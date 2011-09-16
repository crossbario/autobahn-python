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
import de.tavendo.autobahn.WebSocketHandler;
import android.app.Activity;
import android.os.Bundle;
import android.util.Log;

public class Droid1Activity extends Activity {

   static final String TAG = "de.tavendo.autobahn";
//   static final String WSHOST = "192.168.1.132";
   static final String WSHOST = "192.168.2.35";
   static final String WSPORT = "9001";
   static final String WSAGENT = "AutobahnAndroid/0.4.2";

   int currCase = 0;
   int lastCase = 8;
   WebSocketConnection sess = new WebSocketConnection();
   
   private void next() {
      
      try {
         currCase += 1;
         if (currCase <= lastCase) {      
                 sess.connect("ws://" + WSHOST + ":" + WSPORT + "/runCase?case=" + currCase + "&agent=" + WSAGENT,
                       new WebSocketHandler() {
      
                          @Override
                          public void onClose() {
                             Log.d(TAG, "Test case " + currCase + " finished.");
                             next();
                          }            
                 });
         } else {
               sess.connect("ws://" + WSHOST + ":" + WSPORT + "/updateReports?agent=" + WSAGENT,
                     new WebSocketHandler() {
    
                        @Override
                        public void onClose() {
                           Log.d(TAG, "Test reports updated.");
                        }            
               });
         }
      } catch (WebSocketException e) {
         
         Log.d(TAG, e.toString());
      }
   }
   
   @Override
   public void onCreate(Bundle savedInstanceState) {
      super.onCreate(savedInstanceState);
      setContentView(R.layout.main);
      
      next();
      
/*      
      try {
       //sess.connect("ws://192.168.1.130:9000");
       //sess.connect("ws://192.168.2.35:9000");
         sess.connect("ws://192.168.1.132:9001/runCase?case=2&agent=AutobahnAndroid/0.4.2",
               new WebSocketHandler() {

                  @Override
                  public void onClose() {
                     Log.d(TAG, "WebSocket Connection Closed");
                  }            
         });
         
         //sess.send("Hallo, Arsch!!");
         //sess.send("A second message.");
         //sess.send("My last word!");
         //sess.send("NSDSFSDFHASDFKJDSHGFSDHGFJKSDHGF");
      } catch (WebSocketException e) {
         
         Log.d(TAG, e.toString());
      }
*/
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