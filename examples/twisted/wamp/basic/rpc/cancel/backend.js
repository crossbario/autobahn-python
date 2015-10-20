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
   realm: 'realm1'}
);

connection.onopen = function (session) {

   function ping() {      
   }

   function add2(args) {
      return args[0] + args[1];
   }

   function stars(args, kwargs) {
      kwargs = kwargs || {};
      kwargs.nick = kwargs.nick || "somebody";
      kwargs.stars = kwargs.stars || 0;
      return kwargs.nick + " starred " + kwargs.stars + "x";
   }

   var _orders = [];
   for (var i = 0; i < 50; ++i) _orders.push(i);

   function orders(args, kwargs) {
      kwargs = kwargs || {};
      kwargs.limit = kwargs.limit || 5;
      return _orders.slice(0, kwargs.limit);
   }

   function arglen(args, kwargs) {
      args = args || [];
      kwargs = kwargs || {};
      return [args.length, Object.keys(kwargs).length];
   }

   var dl = [];

   dl.push(session.register('com.arguments.ping', ping));
   dl.push(session.register('com.arguments.add2', add2));
   dl.push(session.register('com.arguments.stars', stars));
   dl.push(session.register('com.arguments.orders', orders));
   dl.push(session.register('com.arguments.arglen', arglen));

   when.all(dl).then(
      function () {
         console.log("All registered.");
      },
      function () {
         console.log("Registration failed!", arguments);
      });  
};

connection.open();
