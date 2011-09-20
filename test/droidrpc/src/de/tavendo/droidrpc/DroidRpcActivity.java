package de.tavendo.droidrpc;

import java.util.ArrayList;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import de.tavendo.autobahn.Autobahn;
import de.tavendo.autobahn.AutobahnConnection;

public class DroidRpcActivity extends Activity {

   static final String TAG = "de.tavendo.droidrpc";

   @Override
   public void onCreate(Bundle savedInstanceState) {
      super.onCreate(savedInstanceState);
      setContentView(R.layout.main);

      final AutobahnConnection sess = new AutobahnConnection();

      sess.connect("ws://192.168.1.132:9000", new Autobahn.OnSession() {

         @Override
         public void onOpen() {
            Log.d(TAG, "Autobahn session opened");

            ArrayList<Integer> nums = new ArrayList<Integer>();
            for (int i = 0; i < 100; ++i) nums.add(i);
            sess.call("http://example.com/simple/calc#asum", Integer.class, new Autobahn.OnCallResult() {

               @Override
               public void onResult(Object result) {
                  int res = (Integer) result;
                  Log.d(TAG, "Result == " + res);
               }

               @Override
               public void onError(String errorId, String errorInfo) {
                  Log.d(TAG, "RPC Error - " + errorInfo);
               }
            }, nums);

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
         public void onClose(int code, String reason) {
            Log.d(TAG, "Autobahn session closed (" + code + " - " + reason + ")");
         }
      });
   }
}