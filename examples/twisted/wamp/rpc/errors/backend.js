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

   function sqrt(args) {
      var x = args[0];
      if (x === 0) {
         throw "don't ask foolish questions;)";
      }
      var res = Math.sqrt(x);
      if (res !== res) {
         //throw "cannot take sqrt of negative";
         throw new autobahn.Error('com.myapp.error', ['fuck'], {a: 23, b: 9});
      }
      return res;
   }

   session.register('com.myapp.sqrt', sqrt).then(
      function (registration) {
         console.log("Procedure registered:", registration.id);
      },
      function (error) {
         console.log("Registration failed:", error);
      }
   );
};

connection.open();
