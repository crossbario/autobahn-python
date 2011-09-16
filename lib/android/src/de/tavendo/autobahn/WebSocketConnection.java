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
import android.os.Message;
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
      mWriterHandler.forward(new WebSocketMessage.TextMessage(payload));
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
            mMasterHandler = new Handler() {
               
               public void handleMessage(Message msg) {

                  if (msg.obj instanceof WebSocketMessage.TextMessage) {
                     
                     WebSocketMessage.TextMessage textMessage = (WebSocketMessage.TextMessage) msg.obj;
                     
                     Log.d(TAG, "WebSockets Text message received ('" + textMessage.mPayload + "')");
                     
                  } else if (msg.obj instanceof WebSocketMessage.BinaryMessage) {
                     
                     WebSocketMessage.BinaryMessage binaryMessage = (WebSocketMessage.BinaryMessage) msg.obj;
                     
                     Log.d(TAG, "WebSockets Binary message received (length " + binaryMessage.mPayload.length + ")");
                     
                  } else if (msg.obj instanceof WebSocketMessage.Ping) {
                     
                     WebSocketMessage.Ping ping = (WebSocketMessage.Ping) msg.obj;
                     Log.d(TAG, "WebSockets Ping received");
                     
                     // reply with Pong
                     WebSocketMessage.Pong pong = new WebSocketMessage.Pong();
                     pong.mPayload = ping.mPayload;
                     mWriterHandler.forward(pong);
                     
                  } else if (msg.obj instanceof WebSocketMessage.Pong) {
                     
                     WebSocketMessage.Pong pong = (WebSocketMessage.Pong) msg.obj;
                     Log.d(TAG, "WebSockets Pong received");
                     
                  } else if (msg.obj instanceof WebSocketMessage.Close) {
                     
                     WebSocketMessage.Close close = (WebSocketMessage.Close) msg.obj;
                     Log.d(TAG, "WebSockets Close received");
                                          
                  } else if (msg.obj instanceof WebSocketMessage.ServerHandshake) {
                     
                     WebSocketMessage.ServerHandshake serverHandshake = (WebSocketMessage.ServerHandshake) msg.obj;
                     Log.d(TAG, "WebSockets Server handshake received");
                     
                  } else if (msg.obj instanceof WebSocketMessage.ProtocolViolation) {
                     
                     WebSocketMessage.ProtocolViolation protocolViolation = (WebSocketMessage.ProtocolViolation) msg.obj;
                     Log.d(TAG, "WebSockets Protocol Violation (" + protocolViolation.mReason + ")");
                     
                  } else if (msg.obj instanceof WebSocketMessage.Error) {
                     
                     WebSocketMessage.Error error = (WebSocketMessage.Error) msg.obj;
                     Log.d(TAG, "WebSockets Error (" + error.mException.toString() + ")");
                     
                  } else {
                     
                  }
               }
            };
            
            // create WebSocket reader and thread
            mReaderThread = new WebSocketReader(mMasterHandler, mTransportChannel);
            mReaderThread.start();

            // create WebSocket writer and thread
            mWriterThread = new HandlerThread("WebSocketWriter");
            mWriterThread.start();
            mWriterHandler = new WebSocketWriter(mWriterThread.getLooper(), mMasterHandler, mTransportChannel);
            
            // start WebSockets handshake
            WebSocketMessage.ClientHandshake hs = new WebSocketMessage.ClientHandshake(mWsHost);
            hs.mPath = mWsPath;
            mWriterHandler.forward(hs);
            
         } else {

            throw new WebSocketException("could not connect to WebSockets server");
         }
      } catch (IOException e) {

         throw new WebSocketException("could not connect to WebSockets server (" + e.toString() + ")");
      }

   }

}
