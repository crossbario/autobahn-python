package de.tavendo.droidrpc;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import de.tavendo.autobahn.Autobahn;
import de.tavendo.autobahn.AutobahnConnection;
import de.tavendo.autobahn.AutobahnConnection.OnSession;
import de.tavendo.autobahn.WebSocketException;

public class DroidRpcActivity extends Activity {

   static final String TAG = "de.tavendo.droidrpc";

   @Override
   public void onCreate(Bundle savedInstanceState) {
      super.onCreate(savedInstanceState);
      setContentView(R.layout.main);

      final AutobahnConnection sess = new AutobahnConnection();

      try {

         sess.connect("ws://192.168.1.132:9000", new OnSession() {

            @Override
            public void onOpen() {
               Log.d(TAG, "Autobahn session opened");

               sess.call("http://example.com/simple/calc#add", Integer.class, new Autobahn.OnCallResult() {

                  @Override
                  public void onResult(Object result) {
                     int res = (Integer) result;
                     Log.d(TAG, "Result == " + res);
                  }

                  @Override
                  public void onError(String errorId, String errorInfo) {
                     Log.d(TAG, "RPC Error - " + errorInfo);
                  }
               }, 23, 55);
            }

            @Override
            public void onClose() {
               Log.d(TAG, "Autobahn session closed");
            }
         });

      } catch (WebSocketException e) {
         // TODO Auto-generated catch block
         e.printStackTrace();
      }
   }
}