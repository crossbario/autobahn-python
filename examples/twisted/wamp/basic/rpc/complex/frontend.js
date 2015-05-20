try {
   var autobahn = require('autobahn');
   var when = require('when');
} catch (e) {
   // When running in browser, AutobahnJS will
   // be included without a module system
   var when = autobahn.when;
}

var connection = new autobahn.Connection({
   url: 'ws://127.0.0.1:8080/ws',
   realm: 'crossbardemo'}
);

connection.onopen = function (session) {

   var dl = [];

   dl.push(session.call('com.myapp.add_complex', [2, 3, 4, 5]).then(
      function (res) {
         console.log("Result: " + res.kwargs.c + " + " + res.kwargs.ci + "i");
      }
   ));

   dl.push(session.call('com.myapp.split_name', ['Homer Simpson']).then(
      function (res) {
         console.log("Forename: " + res.args[0] + ", Surname: " + res.args[1]);
      }
   ));

   when.all(dl).then(function () {
      console.log("All finished.");
      connection.close();
   });
};

connection.open();
