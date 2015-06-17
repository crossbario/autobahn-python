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

   session.call('com.myapp.longop', [3], {}, {receive_progress: true}).then(
      function (res) {
         console.log("Final:", res);
         connection.close();
      },
      function (err) {
      },
      function (progress) {
         console.log("Progress:", progress);
      }
   );
};

connection.open();
