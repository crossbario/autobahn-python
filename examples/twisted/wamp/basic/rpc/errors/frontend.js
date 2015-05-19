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

   dl = [];

   var vals1 = [2, 0, -2];
   for (var i = 0; i < vals1.length; ++i) {

      dl.push(session.call('com.myapp.sqrt', [vals1[i]]).then(
         function (res) {
            console.log("Result:", res);
         },
         function (err) {
            console.log("Error:", err.error, err.args, err.kwargs);
         }
      ));
   }

   when.all(dl).then(function () {
      console.log("All finished.");
      connection.close();
   });
};

connection.open();
