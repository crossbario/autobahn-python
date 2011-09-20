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

import java.util.Random;
import java.util.concurrent.ConcurrentHashMap;

import org.codehaus.jackson.type.TypeReference;

import android.os.HandlerThread;
import android.util.Log;

public class AutobahnConnection extends WebSocketConnection implements Autobahn {

   private static final String TAG = "de.tavendo.autobahn.AutobahnConnection";

   protected AutobahnWriter mWriterHandler;

   private final Random mRng = new Random();

   private static final char[] mBase64Chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
         .toCharArray();

   public static class CallResultMeta {

      CallResultMeta(OnCallResult handler, Class<?> resultClass) {
         this.mResultHandler = handler;
         this.mResultClass = resultClass;
         this.mResultTypeRef = null;
      }

      CallResultMeta(OnCallResult handler, TypeReference<?> resultTypeReference) {
         this.mResultHandler = handler;
         this.mResultClass = null;
         this.mResultTypeRef = resultTypeReference;
      }

      public OnCallResult mResultHandler;
      public Class<?> mResultClass;
      public TypeReference<?> mResultTypeRef;
   }

   private final ConcurrentHashMap<String, CallResultMeta> mCalls = new ConcurrentHashMap<String, CallResultMeta>();

   private Autobahn.OnSession mSessionHandler;

   public AutobahnConnection() {
   }

   protected void createWriter() {
      mWriterThread = new HandlerThread("AutobahnWriter");
      mWriterThread.start();
      mWriter = new AutobahnWriter(mWriterThread.getLooper(), mMasterHandler, mTransportChannel, mOptions);
   }

   protected void createReader() {
      mReader = new AutobahnReader(mCalls, mMasterHandler, mTransportChannel, mOptions, "AutobahnReader");
      mReader.start();
   }

   /**
    * Create new random ID, i.e. for use in RPC calls to correlate
    * call message with result message.
    */
   private String newId(int len) {
      char[] buffer = new char[len];
      for (int i = 0; i < len; i++) {
         buffer[i] = mBase64Chars[mRng.nextInt(mBase64Chars.length)];
      }
      return new String(buffer);
   }

   /**
    * Create new random ID of default length.
    */
   private String newId() {
      return newId(8);
   }


   public void connect(String wsUri, Autobahn.OnSession sessionHandler) {

      WebSocketOptions options = new WebSocketOptions();
      options.setReceiveTextMessagesRaw(true);
      options.setMaxMessagePayloadSize(4*1024*1024);
      options.setMaxFramePayloadSize(4*1024*1024);
      options.setTcpNoDelay(false);

      mSessionHandler = sessionHandler;

      try {
         connect(wsUri, new WebSocketHandler() {

            @Override
            public void onOpen() {
               if (mSessionHandler != null) {
                  mSessionHandler.onOpen();
               }
            }

            @Override
            public void onClose() {
               if (mSessionHandler != null) {
                  mSessionHandler.onClose(Autobahn.OnSession.CLOSE_NORMAL, "connection closed normally");
               }
            }


         }, options);

      } catch (WebSocketException e) {

         if (mSessionHandler != null) {
            mSessionHandler.onClose(Autobahn.OnSession.CLOSE_CANNOT_CONNECT, e.toString());
         }
      }

   }

   public void disconnect() {

   }

   protected void processAppMessage(Object message) {

      if (message instanceof AutobahnMessage.CallResult) {

         AutobahnMessage.CallResult callresult = (AutobahnMessage.CallResult) message;

         if (mCalls.containsKey(callresult.mCallId)) {
            CallResultMeta meta = mCalls.get(callresult.mCallId);
            if (meta.mResultHandler != null) {
               meta.mResultHandler.onResult(callresult.mResult);
            }
            mCalls.remove(callresult.mCallId);
         }

      } else if (message instanceof AutobahnMessage.CallError) {

         AutobahnMessage.CallError callerror = (AutobahnMessage.CallError) message;

         if (mCalls.containsKey(callerror.mCallId)) {
            CallResultMeta meta = mCalls.get(callerror.mCallId);
            if (meta.mResultHandler != null) {
               meta.mResultHandler.onError(callerror.mErrorUri, callerror.mErrorDesc);
            }
            mCalls.remove(callerror.mCallId);
         }
      } else {

         Log.d(TAG, "unknown message in AutobahnConnection.processAppMessage");
      }
   }


   public void call(String procUri, CallResultMeta resultMeta, Object... arguments) {

      AutobahnMessage.Call call = new AutobahnMessage.Call(newId(), procUri, arguments.length);
      for (int i = 0; i < arguments.length; ++i) {
         call.mArgs[i] = arguments[i];
      }

      mCalls.put(call.mCallId, resultMeta);

      mWriter.forward(call);
   }

   public void call(String procUri, Class<?> resultType, OnCallResult resultHandler, Object... arguments) {

      call(procUri, new CallResultMeta(resultHandler, resultType), arguments);
   }

   public void call(String procUri, TypeReference<?> resultType, OnCallResult resultHandler, Object... arguments) {

      call(procUri, new CallResultMeta(resultHandler, resultType), arguments);
   }

}
