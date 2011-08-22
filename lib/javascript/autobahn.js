var ab = window["ab"] = {};

ab.version = "0.3.2";

ab._idchars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
ab._idlen = 16;

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

ab.Foo = function() {
   this.x = 0;
}

ab.Foo.prototype.value = function() {
   return this.x;
}

ab.Foo.prototype.add = function(y) {
   this.x += y;
}


ab.Session = function(wsuri, onopen, onclose) {

   var self = this;
   self._wsuri = wsuri;
   self._websocket_onopen = onopen;
   self._websocket_onclose = onclose;
   self._websocket = null;
   self._websocket_connected = false;
   self._calls = new Array();
   self._subscriptions = new Array();

   if ("WebSocket" in window) {
      self._websocket = new WebSocket(self._wsuri);
   }
   else {
      // Firefox 7/8 currently prefixes the WebSocket object
      self._websocket = new MozWebSocket(self._wsuri);
   }

   self._websocket.onmessage = function(e)
   {
      if (ab._debug) {
         console.log("Autobahn RX " + e.data);
      }

      o = JSON.parse(e.data);
      if (o[1] in self._calls)
      {
         if (o[0] == "CALL_RESULT") {
            self._calls[o[1]].resolve(o[2]);
         }
         else if (o[0] == "CALL_ERROR") {
            self._calls[o[1]].reject(o[2]);
         }
         delete self._calls[o[1]];
      }
      else if (o[1] in self._subscriptions)
      {
         if (o[0] == "EVENT") {
            d = $.Deferred();
            self._subscriptions[o[1]].resolve(o[2], d);
            self._subscriptions[o[1]] = d;
         }
      }
   }

   self._websocket.onopen = function(e)
   {
      if (ab._debug) {
         console.log("Autobahn connected to " + self._wsuri + ".");
      }
      self._websocket_connected = true;
      if (self._websocket_onopen != null) self._websocket_onopen();
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


ab.Session.prototype.call = function(procid, arg) {

   self = this;

   if (!self._websocket_connected) throw "Autobahn not connected";

   d = $.Deferred();
   while (true) {
      callid = ab._newid();
      if (!(callid in self._calls)) break;
   }
   self._calls[callid] = d;

   msg = JSON.stringify(["CALL", procid, callid, arg]);
   self._websocket.send(msg);

   if (ab._debug) {
      console.log("Autobahn TX " + msg);
   }

   return d;
}


ab.Session.prototype.subscribe = function(eventid) {

   console.log("SUBSCRIBE " + eventid);

   self = this;

   if (!self._websocket_connected) throw "Autobahn not connected";
   if (eventid in self._subscriptions) throw "already subscribed";

   d = $.Deferred();
   self._subscriptions[eventid] = d;

   msg = JSON.stringify(["SUBSCRIBE", eventid]);
   self._websocket.send(msg);

   if (ab._debug) {
      console.log("Autobahn TX " + msg);
   }
   return d;
}

ab.Session.prototype.publish = function(eventid, event) {

   self = this;
   if (!self._websocket_connected) throw "Autobahn not connected";

   msg = JSON.stringify(["PUBLISH", eventid, event]);
   self._websocket.send(msg);

   if (ab._debug) {
      console.log("Autobahn TX " + msg);
   }
}
