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

   session.register(ping, 'com.arguments.ping')
   session.register(add2, 'com.arguments.add2')
   session.register(stars, 'com.arguments.stars')
   session.register(orders, 'com.arguments.orders')
   session.register(arglen, 'com.arguments.arglen')
};

connection.open();
