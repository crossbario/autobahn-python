try {
   var autobahn = require('autobahn');
} catch (e) {
   // when running in browser, AutobahnJS will
   // be included without a module system
}

var connection = new autobahn.Connection({
   url: 'ws://127.0.0.1:9000/',
   realm: 'realm1'}
);

connection.onopen = function (session) {

   var counter = 0;

   setInterval(function () {
      session.publish('com.myapp.topic1', [counter]);
      counter += 1;
   }, 1000);
};

connection.open();
