package de.tavendo.droidrpc;

import android.app.Activity;
import android.os.Bundle;
import de.tavendo.autobahn.AutobahnConnection;

public class DroidRpcActivity extends Activity {

   static final String TAG = "de.tavendo.droidrpc";

   @Override
   public void onCreate(Bundle savedInstanceState) {
      super.onCreate(savedInstanceState);
      setContentView(R.layout.main);

      AutobahnConnection sess = new AutobahnConnection();
   }
}