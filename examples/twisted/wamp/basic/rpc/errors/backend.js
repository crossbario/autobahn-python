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

   function sqrt(args) {
      var x = args[0];
      if (x === 0) {
         throw "don't ask folly questions;)";
      }
      var res = Math.sqrt(x);
      if (res !== res) {
         //throw "cannot take sqrt of negative";
         throw new autobahn.Error('com.myapp.error', ['fuck'], {a: 23, b: 9});
      }
      return res;
   }

   session.register('com.myapp.sqrt', sqrt);
};

connection.open();
