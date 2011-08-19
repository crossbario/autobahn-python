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

ab._calls = new Array();
ab._websocket = null;
ab._wsuri = null
ab._websocket_connected = false;

ab.open = function(wsuri) {

   if ("WebSocket" in window) {
      ab._websocket = new WebSocket(wsuri);
   }
   else {
      // Firefox 7/8 currently prefixes the WebSocket object
      ab._websocket = new MozWebSocket(wsuri);
   }
   ab._wsuri = wsuri;

   ab._websocket.onmessage = function(e)
   {
      o = JSON.parse(e.data);
      if (o[1] in ab._calls)
      {
         if (o[0] == "CALL_RESULT") {
            ab._calls[o[1]].resolve(o[2]);
         }
         else if (o[0] == "CALL_ERROR") {
            ab._calls[o[1]].reject(o[2]);
         }
         else {
            // unknown message type
         }
         delete ab._calls[o[1]];
      }
   }

   ab._websocket.onopen = function(e)
   {
      console.log("Autobahn connected to " + ab._wsuri + ".");
      ab._websocket_connected = true;
   }

   ab._websocket.onclose = function(e)
   {
      if (ab._websocket_connected) {
         console.log("Autobahn connection to " + ab._wsuri + " lost.");
      } else {
         console.log("Autobahn could not connect to " + ab._wsuri + ".");
      }
      ab._websocket_connected = false;
      ab._wsuri = null;
   }

};

ab.call = function(procid, arg) {
   if (!ab._websocket_connected) throw "Autobahn not connected";
   d = $.Deferred();
   while (true) {
      callid = ab._newid();
      if (!(callid in ab._calls)) break;
   }
   ab._calls[callid] = d;
   msg = JSON.stringify(["CALL", procid, callid, arg]);
   ab._websocket.send(msg);
   return d;
}
