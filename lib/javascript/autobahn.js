var ab = window["ab"] = {};

ab.version = "0.4.3";

ab._idchars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
ab._idlen = 16;
ab._subprotocol = "wamp";

ab._newid = function() {
   var id = "";
   for (var i = 0; i < ab._idlen; ++i) {
     id += ab._idchars.charAt(Math.floor(Math.random() * ab._idchars.length));
   }
   return id;
}

ab._debug = false;

ab.debug = function(enable) {
   ab._debug = enable;
}


ab.PrefixMap = function() {

   var self = this;
   self._index = new Array();
   self._rindex = new Array();
}

ab.PrefixMap.prototype.get = function(prefix) {

   var self = this;
   return self._index[prefix];
}

ab.PrefixMap.prototype.set = function(prefix, uri) {

   var self = this;
   self._index[prefix] = uri;
   self._rindex[uri] = prefix;
}

ab.PrefixMap.prototype.setDefault = function(uri) {

   var self = this;
   self._index[""] = uri;
   self._rindex[uri] = "";
}

ab.PrefixMap.prototype.remove = function(prefix) {

   var self = this;
   uri = self._idnex[prefix];
   if (uri) {
      delete self._index[prefix];
      delete self._rindex[uri];
   }
}

ab.PrefixMap.prototype.resolve = function(curie) {

   var self = this;
   var i = curie.indexOf(":");
   if (i >= 0) {
      prefix = curie.substring(0, i);
      if (self._index[prefix]) {
         return self._index[prefix] + curie.substring(i + 1);
      }
   }
   return null;
}

ab.PrefixMap.prototype.resolveOrPass = function(curieOrUri) {

   var self = this;
   var u = self.resolve(curieOrUri);
   if (u) {
      return u;
   } else {
      return curieOrUri;
   }
}

ab.PrefixMap.prototype.shrink = function(uri) {

   var self = this;
   for (var i = uri.length; i > 0; --i) {
      u = uri.substring(0, i);
      p = self._rindex[u];
      if (p) {
         return p + ":" + uri.substring(i);
      }
   }
   return uri;
}


ab._MESSAGE_TYPEID_NULL           = 0;
ab._MESSAGE_TYPEID_PREFIX         = 1;
ab._MESSAGE_TYPEID_CALL           = 2;
ab._MESSAGE_TYPEID_CALL_RESULT    = 3;
ab._MESSAGE_TYPEID_CALL_ERROR     = 4;
ab._MESSAGE_TYPEID_SUBSCRIBE      = 5;
ab._MESSAGE_TYPEID_UNSUBSCRIBE    = 6;
ab._MESSAGE_TYPEID_PUBLISH        = 7;
ab._MESSAGE_TYPEID_EVENT          = 8;


ab.Session = function(wsuri, onopen, onclose) {

   var self = this;

   self._wsuri = wsuri;
   self._websocket_onopen = onopen;
   self._websocket_onclose = onclose;
   self._websocket = null;
   self._websocket_connected = false;
   self._calls = new Array();
   self._subscriptions = new Array();
   self._prefixes = new ab.PrefixMap();

   if ("WebSocket" in window) {
      self._websocket = new WebSocket(self._wsuri, [ab._subprotocol]);
   }
   else {
      // Firefox 7/8 currently prefixes the WebSocket object
      self._websocket = new MozWebSocket(self._wsuri, [ab._subprotocol]);
   }

   self._websocket.onmessage = function(e)
   {
      if (ab._debug) {
         console.log("Autobahn RX " + e.data);
      }

      o = JSON.parse(e.data);
      if (o[1] in self._calls)
      {
         if (o[0] == ab._MESSAGE_TYPEID_CALL_RESULT) {
            self._calls[o[1]].resolve(o[2]);
         }
         else if (o[0] == ab._MESSAGE_TYPEID_CALL_ERROR) {
            self._calls[o[1]].reject(o[2], o[3], o[4]);
         }
         delete self._calls[o[1]];
      }
      else if (o[0] == ab._MESSAGE_TYPEID_EVENT)
      {
         var subid = self._prefixes.resolveOrPass(o[1]);
         if (subid in self._subscriptions) {
            self._subscriptions[subid](o[1], o[2]);
         }
      }
   }

   self._websocket.onopen = function(e)
   {
      if (self._websocket.protocol != ab._subprotocol) {
         self._websocket.close(1000, "server does not speak WAMP");
         throw "server does not speak WAMP";
      } else {
         if (ab._debug) {
            console.log("Autobahn connected to " + self._wsuri + ".");
         }
         self._websocket_connected = true;
         if (self._websocket_onopen != null) self._websocket_onopen();
      }
   }

   self._websocket.onerror = function(e)
   {
      console.log("onerror");
      console.log(e);
   }

   self._websocket.onclose = function(e)
   {
      if (ab._websocket_connected) {
         console.log("Autobahn connection to " + self._wsuri + " lost.");
      } else {
         console.log("Autobahn could not connect to " + self._wsuri + ".");
      }
      if (self._websocket_onclose != null) self._websocket_onclose();
      self._websocket_connected = false;
      self._wsuri = null;
      self._websocket_onopen = null;
      self._websocket_onclose = null;
   }
}


ab.Session.prototype.prefix = function(prefix, uri) {

   self = this;

   if (!self._websocket_connected) throw "Autobahn not connected";

   msg = JSON.stringify([ab._MESSAGE_TYPEID_PREFIX, prefix, uri]);
   self._websocket.send(msg);

   self._prefixes.set(prefix, uri);

   if (ab._debug) {
      console.log("Autobahn TX " + msg);
   }
}


ab.Session.prototype.call = function() {

   self = this;

   if (!self._websocket_connected) throw "Autobahn not connected";

   d = $.Deferred();
   while (true) {
      callid = ab._newid();
      if (!(callid in self._calls)) break;
   }
   self._calls[callid] = d;

   procuri = arguments[0];
   obj = [ab._MESSAGE_TYPEID_CALL, callid, procuri];
   for (var i = 1; i < arguments.length; ++i) {
      obj.push(arguments[i]);
   }

   msg = JSON.stringify(obj);
   self._websocket.send(msg);

   if (ab._debug) {
      console.log("Autobahn TX " + msg);
   }

   return d;
}


ab.Session.prototype.subscribe = function(topicuri, callback) {

   self = this;
   if (!self._websocket_connected) throw "Autobahn not connected";

   var rtopicuri = self._prefixes.resolveOrPass(topicuri);
   if (rtopicuri in self._subscriptions) throw "already subscribed";

   self._subscriptions[rtopicuri] = callback;

   msg = JSON.stringify([ab._MESSAGE_TYPEID_SUBSCRIBE, topicuri]);
   self._websocket.send(msg);

   if (ab._debug) {
      console.log("Autobahn TX " + msg);
   }
}


ab.Session.prototype.unsubscribe = function(topicuri) {

   self = this;
   if (!self._websocket_connected) throw "Autobahn not connected";

   var rtopicuri = self._prefixes.resolveOrPass(topicuri);
   if (!(rtopicuri in self._subscriptions)) throw "not subscribed";

   delete self._subscriptions[rtopicuri];

   msg = JSON.stringify([ab._MESSAGE_TYPEID_UNSUBSCRIBE, topicuri]);
   self._websocket.send(msg);

   if (ab._debug) {
      console.log("Autobahn TX " + msg);
   }
}


ab.Session.prototype.publish = function(topicuri, event, excludeMe) {

   self = this;
   if (!self._websocket_connected) throw "Autobahn not connected";

   excludeMe = typeof(excludeMe) != 'undefined' ? excludeMe : true;

   msg = JSON.stringify([ab._MESSAGE_TYPEID_PUBLISH, topicuri, event, excludeMe]);
   self._websocket.send(msg);

   if (ab._debug) {
      console.log("Autobahn TX " + msg);
   }
}
