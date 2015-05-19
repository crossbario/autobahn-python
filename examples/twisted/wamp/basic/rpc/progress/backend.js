try {
   var autobahn = require('autobahn');
   var when = require('when');
} catch (e) {
   // when running in browser, AutobahnJS will
   // be included without a module system
   var when = autobahn.when;
}

var connection = new autobahn.Connection({
   url: 'ws://127.0.0.1:8080/ws',
   realm: 'crossbardemo'}
);

connection.onopen = function (session) {

   function longop(args, kwargs, details) {

      var n = args[0];
      var interval_id = null;

      if (details.progress) {
         var i = 0;
         details.progress([i]);
         i += 1;
         interval_id = setInterval(function () {
            if (i < n) {
               details.progress([i]);
               i += 1;               
            } else {
               clearInterval(interval_id);
            }
         }, 1000);
      }

      var d = when.defer();

      setTimeout(function () {
         d.resolve(n);
      }, 1000 * n);

      return d.promise;
   }

   session.register('com.myapp.longop', longop).then(
      function (registration) {
         console.log("Procedure registered:", registration.id);
      },
      function (error) {
         console.log("Registration failed:", error);
      }
   );
};

connection.open();
