var sess;
var retryCount = 0;
var retryDelay = 1;

var slaves = {};

function onConnect() {
   sess.prefix("api", "http://wsperf.org/api#");
   sess.prefix("event", "http://wsperf.org/event#");

   sess.subscribe("event:slaveConnected", onSlaveConnected);
   sess.subscribe("event:slaveDisconnected", onSlaveDisconnected);

   sess.call("api:getSlaves").then(function (res) {
      for (var i in res) {
         slaves[res[i].id] = res[i];
      }
      ab.log("currently connected slaves", slaves);
   }, ab.log);

   sess.subscribe("event:caseResult", onCaseResult);
};


function onSlaveConnected(topic, event) {
   if (!(event.id in slaves)) {
      slaves[event.id] = event;
      ab.log("new slave connected", event);
   }
};


function onSlaveDisconnected(topic, event) {
   if (event.id in slaves) {
      delete slaves[event.id];
      ab.log("slave disconnected", event);
   }
};


function onCaseResult(topic, event) {
   ab.log("got result: case " + event.runId + " from slave " + event.slaveId, event);
};


function runCase() {

   var cd = {};
   cd.uri = $("#runcase_uri").val();
   cd.count = parseInt($("#runcase_count").val());
   cd.size = parseInt($("#runcase_size").val());
   cd.timeout = parseInt($("#runcase_timeout").val());
   cd.binary = $("#runcase_binary").attr("checked") != undefined;
   cd.sync = $("#runcase_sync").attr("checked") != undefined;
   cd.quantile_count = parseInt($("#runcase_bins").val());
   cd.correctness = 'length';

   sess.call("api:runCase", cd).then(function (runId) {
      ab.log("case " + runId + " started", cd);
   }, ab.log);
};


function connect() {
   var wsuri = "ws://" + window.location.hostname + ":9091";

   //ab.debug(true);

   if (window.WebSocket || window.MozWebSocket) {
      sess = new ab.Session(wsuri,
         function() {

            updateStatusline("Connected to " + wsuri);
            retryCount = 0;
            onConnect();
         },
         function() {

            retryCount = retryCount + 1;
            updateStatusline("Connection lost. Reconnecting (" + retryCount + ") ..");
            window.setTimeout(connect, retryDelay * 1000);
         }
      );
   } else {
      //window.location = "/appliance/unsupportedbrowser";
      alert("Browser does not support WebSockets");
   }
}


function updateStatusline(status) {
   $("#statusline").text(status);
};


$(document).ready(function() {

   updateStatusline("Not connected.");
   connect();
});
