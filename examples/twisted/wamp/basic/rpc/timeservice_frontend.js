var autobahn = require('autobahn');

var connection = new autobahn.Connection({
   url: 'ws://127.0.0.1:9000/',
   realm: 'realm1'}
);

connection.onopen = function (session) {

   session.call('com.timeservice.now').then(
      function (now) {
         console.log("Current time:", now);
         connection.close();
      },
      function (error) {
         console.log("Call failed:", error);
         connection.close();
      }
   );
};

connection.open();
