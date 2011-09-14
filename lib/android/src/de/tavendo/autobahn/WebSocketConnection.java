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
import java.net.InetSocketAddress;
import java.net.URISyntaxException;
import java.nio.channels.SocketChannel;

import android.os.Handler;
import android.os.HandlerThread;
import android.util.Log;

import java.net.URI;

public class WebSocketConnection {

   private static final String TAG = "de.tavendo.autobahn.WebSocketConnection";

   private Handler mMasterHandler;

   private WebSocketReader mReaderThread;

   private HandlerThread mWriterThread;
   // private TransportWriter mWriterHandler;
   private WebSocketWriter mWriterHandler;

   private SocketChannel mTransportChannel;

   private URI mWsUri;
   private String mWsScheme;
   private String mWsHost;
   private int mWsPort;
   private String mWsPath;

   public WebSocketConnection() {
   }
   
   public void send(String payload) {
      mWriterHandler.forwardMessage(new WebSocketMessage.TextMessage(payload));
   }

   public void connect(String wsUri) throws WebSocketException {
      
      // don't connect if already connected .. user needs to disconnect first
      //
      if (mTransportChannel != null && mTransportChannel.isConnected()) {
         throw new WebSocketException("already connected");
      }

      // parse WebSockets URI
      //
      try {
         mWsUri = new URI(wsUri);

         if (!mWsUri.getScheme().equals("ws") && !mWsUri.getScheme().equals("wss")) {
            throw new WebSocketException("unsupported scheme for WebSockets URI");
         }
         
         if (mWsUri.getScheme().equals("wss")) {
            throw new WebSocketException("secure WebSockets not implemented");
         }
         
         mWsScheme = mWsUri.getScheme();
         
         if (mWsUri.getPort() == -1) {
            if (mWsScheme.equals("ws")) {
               mWsPort = 80;
            } else {
               mWsPort = 443;
            }
         } else {
            mWsPort = mWsUri.getPort();
         }
         
         if (mWsUri.getHost() == null) {
            throw new WebSocketException("no host specified in WebSockets URI");
         } else {
            mWsHost = mWsUri.getHost();            
         }

         if (mWsUri.getPath() == null || mWsUri.getPath().equals("")) {
            mWsPath = "/";
         } else {
            mWsPath = mWsUri.getPath();            
         }
         
      } catch (URISyntaxException e) {

         throw new WebSocketException("invalid WebSockets URI");
      }
      
      // connect TCP socket
      // http://developer.android.com/reference/java/nio/channels/SocketChannel.html
      //
      try {
         mTransportChannel = SocketChannel.open();

         //mTransportChannel.configureBlocking(false);
         mTransportChannel.socket().connect(new InetSocketAddress(mWsHost, mWsPort), 1000);
         //mTransportChannel.connect(new InetSocketAddress(mWsHost, mWsPort));

         if (mTransportChannel.isConnected()) {

            Log.d(TAG, "established TCP connection to " + mWsHost + ":" + mWsPort);
            
            //OutputStream os = mTransportChannel.socket().getOutputStream();            
            //os.write("Hello, world!".getBytes("UTF-8"));

            mReaderThread = new WebSocketReader(mMasterHandler, mTransportChannel);
            mReaderThread.start();

            mWriterThread = new HandlerThread("WebSocketWriter");
            mWriterThread.start();
            mWriterHandler = new WebSocketWriter(mWriterThread.getLooper(), mTransportChannel);
            
            WebSocketMessage.ClientHandshake hs = new WebSocketMessage.ClientHandshake();
            hs.mHost = mWsHost;
            hs.mPath = mWsPath;
            mWriterHandler.forwardMessage(hs);
            
         } else {

            throw new WebSocketException("could not connect to WebSockets server");
         }
      } catch (IOException e) {

         throw new WebSocketException("could not connect to WebSockets server (" + e.toString() + ")");
      }

   }

}
