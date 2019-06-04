var wsuri;

if (document.location.origin == "file://") {
   wsuri = "ws://127.0.0.1:8080/ws";

} else {
   wsuri = (document.location.protocol === "http:" ? "ws:" : "wss:") + "//" +
               document.location.host + "/ws";
}

var connection = new autobahn.Connection({
   url: wsuri,
   realm: "realm1"
});

var session = null;

connection.onopen = async function (new_session, details) {
    console.log("Connected", details);
    session = new_session;
};

connection.onclose = function (reason, details) {
   console.log("Connection lost: " + reason, details);
   session = null;
}

connection.open();
