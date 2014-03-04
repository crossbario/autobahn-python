try {
   var autobahn = require('autobahn');
} catch (e) {
   // when running in browser, AutobahnJS will
   // be included without a module system
}

var connection = new autobahn.Connection({
   url: 'ws://127.0.0.1:8080/ws',
   realm: 'realm1'}
);

connection.onopen = function (session) {

   function on_heartbeat(args, kwargs, details) {
      console.log("Got heartbeat (publication ID " + details.publication + ")");
   }

   session.subscribe(on_heartbeat, 'com.myapp.heartbeat');


   function on_topic2(args, kwargs) {
      console.log("Got event:", args, kwargs);
   }

   session.subscribe(on_topic2, 'com.myapp.topic2');


   setTimeout(function () {
      console.log("Closing ..");
      connection.close();
   }, 5000);
};

connection.open();
