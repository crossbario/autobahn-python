var sess;

$(document).ready(function() {

   ab.log("started");

   sess = new ab.Session("ws://localhost:9091", function() {

      ab.log("connected");

      sess.prefix("api", "http://wsperf.org/api#");
      sess.prefix("event", "http://wsperf.org/event#");

      sess.call("api:sum", [1,2,3,4,5,6]).then(ab.log);

      sess.subscribe("event:slaveConnected", onSlaveConnected);
   });

   function onSlaveConnected(topic, event) {
      ab.log("slave connected!");
   };
});
