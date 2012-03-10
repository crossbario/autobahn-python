var sess;

$(document).ready(function() {

   ab.log("started");

   sess = new ab.Session("ws://localhost:9091", function() {

      ab.log("connected");

      sess.prefix("api", "http://wsperf.org/api#");
      sess.prefix("event", "http://wsperf.org/event#");

      sess.call("api:sum", [1,2,3,4,5,6]).then(ab.log);

      sess.subscribe("event:slaveConnected", onSlaveConnected);
      sess.subscribe("event:slaveDisconnected", onSlaveDisconnected);
      sess.subscribe("event:caseResult", onCaseResult);
   });

   function onSlaveConnected(topic, event) {
      ab.log("wsperf slave " + event.ident + "[" + event.id + "] connected.");
      ab.log(event);
   };

   function onSlaveDisconnected(topic, event) {
      ab.log("wsperf slave " + "[" + event.id + "] disconnected.");
      ab.log(event);
   };

   function onCaseResult(topic, event) {
      ab.log("wsperf case result");
      ab.log(event);
   };
});

function runCase() {

   var cd = {};
   cd.size = parseInt($("#runcase_size").val());
   cd.binary = $("#runcase_binary").attr("checked") != undefined;
   ab.log(cd);

   sess.call("api:runCase", cd).always(ab.log);
};
