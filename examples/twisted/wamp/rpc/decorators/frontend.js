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

   var procs = ['com.mathservice.add2',
                'com.mathservice.mul2',
                'com.mathservice.div2'];
   var x = 2;
   var y = 3;

   var dl = [];

   for (var i = 0; i < procs.length; ++i) {

      dl.push(session.call(procs[i], [x, y]).then(
         function (res) {
            console.log(res);
         },
         function (error) {
            console.log(error);
         }
      ));
   }

   when.all(dl).then(function () {
      console.log("All finished.");
      connection.close();
   });  
};

connection.open();
