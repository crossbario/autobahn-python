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

function randint(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

connection.onopen = function (session) {

   var counter = 0;

   setInterval(function () {
      session.publish('com.myapp.heartbeat');

      var obj = {'counter': counter, 'foo': [1, 2, 3]};
      session.publish('com.myapp.topic2', [randint(0, 100), 23], {c: "Hello", d: obj});

      counter += 1;

      console.log("events published");
   }, 1000);
};

connection.open();
