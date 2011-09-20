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

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import de.tavendo.autobahn.WebSocketConnection;
import de.tavendo.autobahn.WebSocketException;
import de.tavendo.autobahn.WebSocketHandler;
import de.tavendo.autobahn.WebSocketOptions;

public class Droid1Activity extends Activity {

   static final String TAG = "de.tavendo.droid1";

   static EditText mHostname;
   static EditText mPort;
   static EditText mAgent;
   static TextView mStatusline;
   static Button mStart;

   int currCase = 0;
   int lastCase = 0;

   WebSocketConnection sess = new WebSocketConnection();

   private void next() {

      try {
         if (currCase == 0) {

            sess.connect("ws://" + mHostname.getText() + ":" + mPort.getText() + "/getCaseCount",
                  new WebSocketHandler() {

                     @Override
                     public void onTextMessage(String payload) {
                        lastCase = Integer.parseInt(payload);
                     }

                     @Override
                     public void onClose() {
                        mStatusline.setText("Ok, will run " + lastCase + " cases.");
                        currCase += 1;
                        next();
                     }
            });

         } else {
            if (currCase <= lastCase) {

                 WebSocketOptions options = new WebSocketOptions();
                 options.setReceiveTextMessagesRaw(true);
                 //options.setValidateIncomingUtf8(false);
                 //options.setMaskClientFrames(false);
                 options.setMaxMessagePayloadSize(4*1024*1024);
                 options.setMaxFramePayloadSize(4*1024*1024);
                 options.setTcpNoDelay(false);

                 sess.connect("ws://" + mHostname.getText() + ":" + mPort.getText() + "/runCase?case=" + currCase + "&agent=" + mAgent.getText(),
                       new WebSocketHandler() {

                          @Override
                          public void onRawTextMessage(byte[] payload) {
                             sess.sendRawTextMessage(payload);
                          }

                          @Override
                          public void onBinaryMessage(byte[] payload) {
                             sess.sendBinaryMessage(payload);
                          }

                          @Override
                          public void onOpen() {
                             mStatusline.setText("Test case " + currCase + "/" + lastCase + " started ..");
                          }

                          @Override
                          public void onClose() {
                             mStatusline.setText("Test case " + currCase + "/" + lastCase + " finished.");
                             currCase += 1;
                             next();
                          }
                 }, options);
            } else {
                  sess.connect("ws://" + mHostname.getText() + ":" + mPort.getText() + "/updateReports?agent=" + mAgent.getText(),
                        new WebSocketHandler() {

                           @Override
                           public void onOpen() {
                              mStatusline.setText("Updating test reports ..");
                           }

                           @Override
                           public void onClose() {
                              mStatusline.setText("Test reports updated. Finished.");
                              mStart.setEnabled(true);
                           }
                  });
            }
         }
      } catch (WebSocketException e) {

         Log.d(TAG, e.toString());
      }
   }

   @Override
   public void onCreate(Bundle savedInstanceState) {

      super.onCreate(savedInstanceState);

      setContentView(R.layout.main);

      mHostname = (EditText) findViewById(R.id.hostname);
      mPort = (EditText) findViewById(R.id.port);
      mAgent = (EditText) findViewById(R.id.agent);
      mStatusline = (TextView) findViewById(R.id.statusline);

      mStart = (Button) findViewById(R.id.start);
      mStart.setOnClickListener(new Button.OnClickListener() {

         @Override
         public void onClick(View v) {
            mStart.setEnabled(false);
            currCase = 0;
            next();
         }

      });
  }

}
