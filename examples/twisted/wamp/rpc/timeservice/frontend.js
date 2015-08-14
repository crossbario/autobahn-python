try {
   var autobahn = require('autobahn');
} catch (e) {
   // when running in browser, AutobahnJS will
   // be included without a module system
}

var connection = new autobahn.Connection({
   url: 'ws://127.0.0.1:8080/ws',
   realm: 'crossbardemo'}
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
