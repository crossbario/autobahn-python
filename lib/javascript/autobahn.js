/******************************************************************************
**
**  Copyright 2011 Tavendo GmbH
**
**  Licensed under the Apache License, Version 2.0 (the "License");
**  you may not use this file except in compliance with the License.
**  You may obtain a copy of the License at
**
**      http://www.apache.org/licenses/LICENSE-2.0
**
**  Unless required by applicable law or agreed to in writing, software
**  distributed under the License is distributed on an "AS IS" BASIS,
**  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
**  See the License for the specific language governing permissions and
**  limitations under the License.
**
******************************************************************************/

/*jshint forin:true,
         noarg:true,
         noempty:true,
         eqeqeq:true,
         bitwise:true,
         strict:true,
         undef:true,
         curly:true,
         browser:true,
         indent:3,
         maxerr:50,
         newcap:true */
/*global window, WebSocket, MozWebSocket, console, $ */

"use strict";

var ab = window.ab = {};

ab.version = "0.4.9";

ab._idchars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
ab._idlen = 16;
ab._subprotocol = "wamp";

ab._newid = function () {
   var id = "";
   for (var i = 0; i < ab._idlen; i += 1) {
      id += ab._idchars.charAt(Math.floor(Math.random() * ab._idchars.length));
   }
   return id;
};

ab.log = function (o) {
   if (window.console && console.log) {
      //console.log.apply(console, !!arguments.length ? arguments : [this]);
      if (arguments.length > 1) {
         console.group("Log Item");
         for (var i = 0; i < arguments.length; i += 1) {
            console.log(arguments[i]);
         }
         console.groupEnd();
      } else {
         console.log(arguments[0]);
      }
   }
}

ab._debugrpc = false;
ab._debugpubsub = false;
ab._debugws = false;

ab.debug = function (enable) {
   if ("console" in window) {
      ab._debugrpc = enable;
      ab._debugpubsub = enable;
   } else {
      throw "browser does not support console object";
   }
};


ab.PrefixMap = function () {

   var self = this;
   self._index = {};
   self._rindex = {};
};

ab.PrefixMap.prototype.get = function (prefix) {

   var self = this;
   return self._index[prefix];
};

ab.PrefixMap.prototype.set = function (prefix, uri) {

   var self = this;
   self._index[prefix] = uri;
   self._rindex[uri] = prefix;
};

ab.PrefixMap.prototype.setDefault = function (uri) {

   var self = this;
   self._index[""] = uri;
   self._rindex[uri] = "";
};

ab.PrefixMap.prototype.remove = function (prefix) {

   var self = this;
   var uri = self._index[prefix];
   if (uri) {
      delete self._index[prefix];
      delete self._rindex[uri];
   }
};

ab.PrefixMap.prototype.resolve = function (curie) {

   var self = this;
   var i = curie.indexOf(":");
   if (i >= 0) {
      var prefix = curie.substring(0, i);
      if (self._index[prefix]) {
         return self._index[prefix] + curie.substring(i + 1);
      }
   }
   return null;
};

ab.PrefixMap.prototype.resolveOrPass = function (curieOrUri) {

   var self = this;
   var u = self.resolve(curieOrUri);
   if (u) {
      return u;
   } else {
      return curieOrUri;
   }
};

ab.PrefixMap.prototype.shrink = function (uri) {

   var self = this;
   for (var i = uri.length; i > 0; i -= 1) {
      var u = uri.substring(0, i);
      var p = self._rindex[u];
      if (p) {
         return p + ":" + uri.substring(i);
      }
   }
   return uri;
};


ab._MESSAGE_TYPEID_WELCOME        = 0;
ab._MESSAGE_TYPEID_PREFIX         = 1;
ab._MESSAGE_TYPEID_CALL           = 2;
ab._MESSAGE_TYPEID_CALL_RESULT    = 3;
ab._MESSAGE_TYPEID_CALL_ERROR     = 4;
ab._MESSAGE_TYPEID_SUBSCRIBE      = 5;
ab._MESSAGE_TYPEID_UNSUBSCRIBE    = 6;
ab._MESSAGE_TYPEID_PUBLISH        = 7;
ab._MESSAGE_TYPEID_EVENT          = 8;


ab.Session = function (wsuri, onopen, onclose) {

   var self = this;

   self._wsuri = wsuri;
   self._websocket_onopen = onopen;
   self._websocket_onclose = onclose;
   self._websocket = null;
   self._websocket_connected = false;
   self._session_id = null;
   self._calls = {};
   self._subscriptions = {};
   self._prefixes = new ab.PrefixMap();

   self._txcnt = 0;
   self._rxcnt = 0;

   if ("WebSocket" in window) {
      // Chrome et. al.
      self._websocket = new WebSocket(self._wsuri, [ab._subprotocol]);
   } else if ("MozWebSocket" in window) {
      // Firefox currently prefixes the WebSocket object
      self._websocket = new MozWebSocket(self._wsuri, [ab._subprotocol]);
   } else {
      throw "browser does not support WebSockets";
   }

   self._websocket.onmessage = function (e)
   {
      if (ab._debugws) {
         self._rxcnt += 1;
         console.group("WAMP Receive");
         console.info(self._wsuri + "  [" + self._session_id + "]");
         console.log(self._rxcnt);
         console.log(e.data);
         console.groupEnd();
      }

      var o = JSON.parse(e.data);
      if (o[1] in self._calls)
      {
         if (o[0] === ab._MESSAGE_TYPEID_CALL_RESULT) {

            var d = self._calls[o[1]];
            var r = o[2];

            if (ab._debugrpc && d._ab_callobj !== undefined) {
               console.group("WAMP Call", d._ab_callobj[2]);
               console.timeEnd(d._ab_tid);
               console.group("Arguments")
               for (var i = 3; i < d._ab_callobj.length; i += 1) {
                  var arg = d._ab_callobj[i];
                  if (arg !== undefined) {
                     console.log(arg);
                  } else {
                     break;
                  }
               }
               console.groupEnd();
               console.group("Result")
               console.log(r);
               console.groupEnd();
               console.groupEnd();
            }

            d.resolve(r);
         }
         else if (o[0] === ab._MESSAGE_TYPEID_CALL_ERROR) {

            var d = self._calls[o[1]];
            var uri = o[2];
            var desc = o[3];
            var detail = o[4];

            if (ab._debugrpc && d._ab_callobj !== undefined) {
               console.group("WAMP Call", d._ab_callobj[2]);
               console.timeEnd(d._ab_tid);
               console.group("Arguments")
               for (var i = 3; i < d._ab_callobj.length; i += 1) {
                  var arg = d._ab_callobj[i];
                  if (arg !== undefined) {
                     console.log(arg);
                  } else {
                     break;
                  }
               }
               console.groupEnd();
               console.group("Error")
               console.log(uri);
               console.log(desc);
               if (detail !== undefined) {
                  console.log(detail);
               }
               console.groupEnd();
               console.groupEnd();
            }

            if (detail !== undefined) {
               d.reject(uri, desc, detail);
            } else {
               d.reject(uri, desc);
            }
         }
         delete self._calls[o[1]];
      }
      else if (o[0] === ab._MESSAGE_TYPEID_EVENT)
      {
         var subid = self._prefixes.resolveOrPass(o[1]);
         if (subid in self._subscriptions) {

            var uri = o[1];
            var val = o[2];

            if (ab._debugpubsub) {
               console.group("WAMP Event");
               console.info(self._wsuri + "  [" + self._session_id + "]");
               console.log(uri);
               console.log(val);
               console.groupEnd();
            }

            self._subscriptions[subid](uri, val);
         }
      }
      else if (o[0] === ab._MESSAGE_TYPEID_WELCOME)
      {
         if (self._session_id === null) {
            self._session_id = o[1];

            if (ab._debugrpc || ab._debugpubsub) {
               console.group("WAMP Welcome");
               console.info(self._wsuri + "  [" + self._session_id + "]");
               console.groupEnd();
            }

            if (self._websocket_onopen !== null) {
               self._websocket_onopen();
            }
         } else {
            throw "protocol error (welcome message received more than once)";
         }
      }
   };

   self._websocket.onopen = function (e)
   {
      if (self._websocket.protocol !== ab._subprotocol) {
         self._websocket.close(1000, "server does not speak WAMP");
         throw "server does not speak WAMP (but '" + self._websocket.protocol + "' !)";
      } else {
         if (ab._debugws) {
            console.group("WAMP Connect");
            console.info(self._wsuri);
            console.log(self._websocket.protocol);
            console.groupEnd();
         }
         self._websocket_connected = true;
      }
   };

   self._websocket.onerror = function (e)
   {
      console.log("onerror");
      console.log(e);
   };

   self._websocket.onclose = function (e)
   {
      if (ab._websocket_connected) {
         console.log("Autobahn connection to " + self._wsuri + " lost.");
      } else {
         console.log("Autobahn could not connect to " + self._wsuri + ".");
      }
      if (self._websocket_onclose !== null) {
         self._websocket_onclose();
      }
      self._websocket_connected = false;
      self._wsuri = null;
      self._websocket_onopen = null;
      self._websocket_onclose = null;
   };
};


ab.Session.prototype._send = function (msg) {

   var self = this;

   if (!self._websocket_connected) {
      throw "Autobahn not connected";
   }

   var rmsg = JSON.stringify(msg);
   self._websocket.send(rmsg);
   self._txcnt += 1;

   if (ab._debugws) {
      console.group("WAMP Transmit");
      console.info(self._wsuri + "  [" + self._session_id + "]");
      console.log(self._txcnt);
      console.log(rmsg);
      console.groupEnd();
   }
}


ab.Session.prototype.sessionid = function () {

   var self = this;
   return self._session_id;
};


ab.Session.prototype.prefix = function (prefix, uri) {

   var self = this;

   self._prefixes.set(prefix, uri);

   if (ab._debugrpc || ab._debugpubsub) {
      console.group("WAMP Prefix");
      console.info(self._wsuri + "  [" + self._session_id + "]");
      console.log(prefix);
      console.log(uri);
      console.groupEnd();
   }

   var msg = [ab._MESSAGE_TYPEID_PREFIX, prefix, uri];
   self._send(msg);
};


ab.Session.prototype.call = function () {

   var self = this;

   var d = new $.Deferred();
   var callid;
   while (true) {
      callid = ab._newid();
      if (!(callid in self._calls)) {
         break;
      }
   }
   self._calls[callid] = d;

   var procuri = arguments[0];
   var obj = [ab._MESSAGE_TYPEID_CALL, callid, procuri];
   for (var i = 1; i < arguments.length; i += 1) {
      obj.push(arguments[i]);
   }

   self._send(obj);

   if (ab._debugrpc) {
      d._ab_callobj = obj;
      d._ab_tid = self._wsuri + "  [" + self._session_id + "][" + callid + "]";
      console.time(d._ab_tid);
      console.info();

   }

   return d;
};


ab.Session.prototype.subscribe = function (topicuri, callback) {

   var self = this;

   var rtopicuri = self._prefixes.resolveOrPass(topicuri);
   if (rtopicuri in self._subscriptions) {
      throw "already subscribed";
   }

   self._subscriptions[rtopicuri] = callback;

   if (ab._debugpubsub) {
      console.group("WAMP Subscribe");
      console.info(self._wsuri + "  [" + self._session_id + "]");
      console.log(topicuri);
      console.log(callback);
      console.groupEnd();
   }

   var msg = [ab._MESSAGE_TYPEID_SUBSCRIBE, topicuri];
   self._send(msg);
};


ab.Session.prototype.unsubscribe = function (topicuri) {

   var self = this;

   var rtopicuri = self._prefixes.resolveOrPass(topicuri);
   var callback;
   if (!(rtopicuri in self._subscriptions)) {
      throw "not subscribed";
   } else {
      callback = self._subscriptions[rtopicuri];
   }

   delete self._subscriptions[rtopicuri];

   if (ab._debugpubsub) {
      console.group("WAMP Unsubscribe");
      console.info(self._wsuri + "  [" + self._session_id + "]");
      console.log(topicuri);
      console.log(callback);
      console.groupEnd();
   }

   var msg = [ab._MESSAGE_TYPEID_UNSUBSCRIBE, topicuri];
   self._send(msg);
};


ab.Session.prototype.publish = function (topicuri, event, excludeMe) {

   var self = this;

   excludeMe = typeof(excludeMe) !== 'undefined' ? excludeMe : true;

   if (ab._debugpubsub) {
      console.group("WAMP Publish");
      console.info(self._wsuri + "  [" + self._session_id + "]");
      console.log(topicuri);
      console.log(event);
      console.log(excludeMe);
      console.groupEnd();
   }

   var msg = [ab._MESSAGE_TYPEID_PUBLISH, topicuri, event, excludeMe];
   self._send(msg);
};
