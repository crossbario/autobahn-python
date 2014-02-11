var autobahn = require('autobahn');

var connection = new autobahn.Connection({
   url: 'ws://127.0.0.1:9000/',
   realm: 'realm1'}
);

connection.onopen = function (session) {

   function utcnow() {
      console.log("Someone is calling me;)");
      now = new Date();
      return now.toISOString();
   }

   session.register(utcnow, 'com.timeservice.now').then(
      function (registration) {
         console.log("Procedure registered:", registration.id);
      },
      function (error) {
         console.log("Registration failed:", error);
      }
   );
};

connection.open();
