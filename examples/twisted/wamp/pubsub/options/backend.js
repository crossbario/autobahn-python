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

   var counter = 0;

   setInterval(function () {

      var options = {acknowledge: true};

      session.publish('com.myapp.topic1', [counter], {}, options).then(
         function (publication) {
            console.log("Event published with publication ID " + publication.id);
         }
      );

      counter += 1;
   }, 1000);
};

connection.open();
