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

   // a "fast" function or a function that returns
   // a direct value (not a promise)
   function square(x) {
      return x * x;
   }

   session.register('com.math.square', square);


   // simulates a "slow" function or a function that
   // returns a promise
   function slowsquare(x) {

      // create a deferred
      var d = when.defer();

      // resolve the promise after 1s
      setTimeout(function () {
         d.resolve(x * x);
      }, 1000);

      // need to return the promise
      return d.promise;
   }

   session.register('com.math.slowsquare', slowsquare).then(
      function (registration) {
         console.log("Procedure registered:", registration.id);
      },
      function (error) {
         console.log("Registration failed:", error);
      }
   );
};

connection.open();
