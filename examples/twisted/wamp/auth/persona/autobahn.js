(function(e){if("function"==typeof bootstrap)bootstrap("autobahn",e);else if("object"==typeof exports)module.exports=e();else if("function"==typeof define&&define.amd)define(e);else if("undefined"!=typeof ses){if(!ses.ok())return;ses.makeAutobahn=e}else"undefined"!=typeof window?window.autobahn=e():global.autobahn=e()})(function(){var define,ses,bootstrap,module,exports;
return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);throw new Error("Cannot find module '"+o+"'")}var f=n[o]={exports:{}};t[o][0].call(f.exports,function(e){var n=t[o][1][e];return s(n?n:e)},f,f.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
// shim for using process in browser

var process = module.exports = {};

process.nextTick = (function () {
    var canSetImmediate = typeof window !== 'undefined'
    && window.setImmediate;
    var canPost = typeof window !== 'undefined'
    && window.postMessage && window.addEventListener
    ;

    if (canSetImmediate) {
        return function (f) { return window.setImmediate(f) };
    }

    if (canPost) {
        var queue = [];
        window.addEventListener('message', function (ev) {
            if (ev.source === window && ev.data === 'process-tick') {
                ev.stopPropagation();
                if (queue.length > 0) {
                    var fn = queue.shift();
                    fn();
                }
            }
        }, true);

        return function nextTick(fn) {
            queue.push(fn);
            window.postMessage('process-tick', '*');
        };
    }

    return function nextTick(fn) {
        setTimeout(fn, 0);
    };
})();

process.title = 'browser';
process.browser = true;
process.env = {};
process.argv = [];

process.binding = function (name) {
    throw new Error('process.binding is not supported');
}

// TODO(shtylman)
process.cwd = function () { return '/' };
process.chdir = function (dir) {
    throw new Error('process.chdir is not supported');
};

},{}],2:[function(require,module,exports){
///////////////////////////////////////////////////////////////////////////////
//
//  AutobahnJS - http://autobahn.ws, http://wamp.ws
//
//  A JavaScript library for WAMP ("The Web Application Messaging Protocol").
//
//  Copyright (C) 2011-2014 Tavendo GmbH, http://tavendo.com
//
//  Licensed under the MIT License.
//  http://www.opensource.org/licenses/mit-license.php
//
///////////////////////////////////////////////////////////////////////////////


var session = require('./session.js');
var websocket = require('./websocket.js');
var connection = require('./connection.js');
var persona = require('./persona.js');

var when = require('when');
//var fn = require("when/function");
var crypto = require('crypto-js');

var pjson = require('../package.json');


exports.version = pjson.version;

exports.WebSocket = websocket.WebSocket;

exports.Connection = connection.Connection;

exports.Session = session.Session;
exports.Invocation = session.Invocation;
exports.Event = session.Event;
exports.Result = session.Result;
exports.Error = session.Error;
exports.Subscription = session.Subscription;
exports.Registration = session.Registration;
exports.Publication = session.Publication;

exports.auth_persona = persona.auth;

exports.when = when;
//exports.fn = fn;
exports.crypto = crypto;

},{"../package.json":44,"./connection.js":3,"./persona.js":4,"./session.js":5,"./websocket.js":6,"crypto-js":15,"when":42}],3:[function(require,module,exports){
///////////////////////////////////////////////////////////////////////////////
//
//  AutobahnJS - http://autobahn.ws, http://wamp.ws
//
//  A JavaScript library for WAMP ("The Web Application Messaging Protocol").
//
//  Copyright (C) 2011-2014 Tavendo GmbH, http://tavendo.com
//
//  Licensed under the MIT License.
//  http://www.opensource.org/licenses/mit-license.php
//
///////////////////////////////////////////////////////////////////////////////

var session = require('./session.js');
var websocket = require('./websocket.js');


var Connection = function (options) {

   var self = this;

   self._options = options;
   self._websocket_factory = new websocket.WebSocket(self._options.url, ['wamp.2.json']);
   self._websocket = null;
   self._retry = false;
   self._retry_count = 0;
   self._session = null;
   self._is_open = false;
};


Connection.prototype.open = function () {

   var self = this;

   self._retry = true;
   self._retry_count = 0;

   function retry () {

      self._websocket = self._websocket_factory.create();
      self._session = new session.Session(self._websocket, self._options);

      self._websocket.onopen = function () {
         self._session.join(self._options.realm);
      };

      self._session.onjoin = function (details) {
         self._is_open = true;
         if (self.onopen) {
            self.onopen(self._session, details);
         }
      };

      // session is open.

      self._session.onleave = function () {
         self._session = null;
         self._is_open = false;
         if (self.onclose) {
            self.onclose();
         }

         self._websocket.close(1000);
      };

      self._websocket.onclose = function () {
         if (self._session) {
            self._session = null;
            self._is_open = false;
            if (self.onclose) {
               self.onclose();
            }
         }
         self._websocket = null;

         self._retry_count += 1;
         if (self._retry && self._retry_count < self._options.max_retries) {
            setTimeout(retry, self._options.retry_delay);
         }
      }
   }

   retry();
};


Connection.prototype.close = function () {
   var self = this;
   self._retry = false;
   self._websocket.close();
};


Object.defineProperty(Connection.prototype, "session", {
   get: function () {
      return this._session;
   }
});


Object.defineProperty(Connection.prototype, "isOpen", {
   get: function () {
      return this._is_open;
   }
});


exports.Connection = Connection;

},{"./session.js":5,"./websocket.js":6}],4:[function(require,module,exports){
///////////////////////////////////////////////////////////////////////////////
//
//  AutobahnJS - http://autobahn.ws, http://wamp.ws
//
//  A JavaScript library for WAMP ("The Web Application Messaging Protocol").
//
//  Copyright (C) 2011-2014 Tavendo GmbH, http://tavendo.com
//
//  Licensed under the MIT License.
//  http://www.opensource.org/licenses/mit-license.php
//
///////////////////////////////////////////////////////////////////////////////

var when = require('when');
var when_fn = require("when/function");


function auth(session, user, extra) {
   // Chrome: https://github.com/mozilla/persona/issues/4083

   var d = when.defer();

   navigator.id.watch({
      loggedInUser: user,
      onlogin: function (assertion) {
         // A user has logged in! Here you need to:
         // 1. Send the assertion to your backend for verification and to create a session.
         // 2. Update your UI.
         d.resolve(assertion);
      },
      onlogout: function() {
         // A user has logged out! Here you need to:
         // Tear down the user's session by redirecting the user or making a call to your backend.
         // Also, make sure loggedInUser will get set to null on the next page load.
         // (That's a literal JavaScript null. Not false, 0, or undefined. null.)
         session.leave();
      }
   });

   return d.promise;
}

exports.auth = auth;

},{"when":42,"when/function":41}],5:[function(require,module,exports){
var global=self;///////////////////////////////////////////////////////////////////////////////
//
//  AutobahnJS - http://autobahn.ws, http://wamp.ws
//
//  A JavaScript library for WAMP ("The Web Application Messaging Protocol").
//
//  Copyright (C) 2011-2014 Tavendo GmbH, http://tavendo.com
//
//  Licensed under the MIT License.
//  http://www.opensource.org/licenses/mit-license.php
//
///////////////////////////////////////////////////////////////////////////////


var when = require('when');
var when_fn = require("when/function");

var crypto = require('crypto-js');

var websocket = require('./websocket.js');


// WAMP "Advanced Profile" support in AutobahnJS:
//
WAMP_FEATURES = {
   roles: {
      caller: {
         features: {
            caller_identification: true,
            progressive_call_results: true
         }
      },
      callee: {
         features: {
            progressive_call_results: true
         }
      },
      publisher: {
         features: {
            subscriber_blackwhite_listing: true,
            publisher_exclusion: true,
            publisher_identification: true
         }
      },
      subscriber: {
         features: {
            publisher_identification: true
         }
      }
   }
};


// generate a WAMP ID
//
function newid () {
   return Math.floor(Math.random() * 9007199254740992);
}


// PBKDF2-base key derivation function for salted WAMP-CRA
//
function derive_key (secret, extra) {
   if (extra && extra.salt) {
      var salt = extra.salt;
      var keylen = extra.keylen || 32;
      var iterations = extra.iterations || 10000;
      var key = crypto.PBKDF2(secret,
                              salt,
                              {
                                 keySize: keylen / 4,
                                 iterations: iterations,
                                 hasher: CryptoJS.algo.SHA256
                              }
      );
      return key.toString(crypto.enc.Base64);
   } else {
      return secret;
   }
}


function auth_sign (challenge, secret) {
   if (!secret) {
      secret = "";
   }

   return crypto.HmacSHA256(challenge, secret).toString(crypto.enc.Base64);
}


var Invocation = function (caller, progress) {

   var self = this;

   self.caller = caller;
   self.progress = progress;
};


var Event = function (publication, publisher) {

   var self = this;

   self.publication = publication;
   self.publisher = publisher;
};


var Result = function (args, kwargs) {

   var self = this;

   self.args = args || [];
   self.kwargs = kwargs || {};
};


var Error = function (error, args, kwargs) {

   var self = this;

   self.error = error;
   self.args = args || [];
   self.kwargs = kwargs || {};
};


var Subscription = function (handler, session, id) {

   var self = this;

   self._handler = handler;
   self._session = session;
   self.active = true;
   self.id = id;
};


Subscription.prototype.unsubscribe = function () {

   var self = this;
   return self._session._unsubscribe(self);
};


var Registration = function (endpoint, session, id) {

   var self = this;

   self._endpoint = endpoint;
   self._session = session;
   self.active = true;
   self.id = id;
};


Registration.prototype.unregister = function () {

   var self = this;
   return self._session._unregister(self);
};


var Publication = function (id) {

   var self = this;
   self.id = id;
};


var MSG_TYPE = {
   HELLO: 1,
   WELCOME: 2,
   ABORT: 3,
   CHALLENGE: 4,
   AUTHENTICATE: 5,
   GOODBYE: 6,
   HEARTBEAT: 7,
   ERROR: 8,
   PUBLISH: 16,
   PUBLISHED: 17,
   SUBSCRIBE: 32,
   SUBSCRIBED: 33,
   UNSUBSCRIBE: 34,
   UNSUBSCRIBED: 35,
   EVENT: 36,
   CALL: 48,
   CANCEL: 49,
   RESULT: 50,
   REGISTER: 64,
   REGISTERED: 65,
   UNREGISTER: 66,
   UNREGISTERED: 67,
   INVOCATION: 68,
   INTERRUPT: 69,
   YIELD: 70
};



var Session = function (socket, options) {

   var self = this;

   // the transport connection (WebSocket object)
   self._socket = socket;

   // options
   self._options = options;

   // the WAMP session ID
   self.id = null;

   // the WAMP realm joined
   self.realm = null;

   // the WAMP features in use
   self._features = null;

   // closing state
   self._goodbye_sent = false;
   self._transport_is_closing = false;

   // outstanding requests;
   self._publish_reqs = {};
   self._subscribe_reqs = {};
   self._unsubscribe_reqs = {};
   self._call_reqs = {};
   self._register_reqs = {};
   self._unregister_reqs = {};

   // subscriptions in place;
   self._subscriptions = {};

   // registrations in place;
   self._registrations = {};

   // incoming invocations;
   self._invocations = {};


   // deferred factory
   if (options && options.use_es6_promises && ('Promise' in global)) {

      // ES6-based deferred factory
      //
      self.defer = function () {
         var deferred = {};

         deferred.promise = new Promise(function (resolve, reject) {
            deferred.resolve = resolve;
            deferred.reject = reject;
         });

         return deferred;
      };

   } else if (options && options.use_deferred) {

      // use explicit deferred factory, e.g. jQuery.Deferred or Q.defer
      //
      self.defer = options.use_deferred;

   } else {

      // whenjs-based deferred factory
      //
      self.defer = when.defer;
   }


   self._send_wamp = function (msg) {
      self._socket.send(JSON.stringify(msg));
   };


   self._protocol_violation = function (reason) {
      console.log("Protocol violation:", reason);
   };

   self._MESSAGE_MAP = {};
   self._MESSAGE_MAP[MSG_TYPE.ERROR] = {};


   self._process_SUBSCRIBED = function (msg) {
      //
      // process SUBSCRIBED reply to SUBSCRIBE
      //
      var request = msg[1];
      var subscription = msg[2];

      if (request in self._subscribe_reqs) {

         var r = self._subscribe_reqs[request];

         var d = r[0];
         var handler = r[1];
         var options = r[2];

         var sub = new Subscription(handler, self, subscription);

         self._subscriptions[subscription] = sub;

         d.resolve(sub);

         delete self._subscribe_reqs[request];

      } else {
         self._protocol_violation("SUBSCRIBED received for non-pending request ID " + request);
      }
   };
   self._MESSAGE_MAP[MSG_TYPE.SUBSCRIBED] = self._process_SUBSCRIBED;


   self._process_SUBSCRIBE_ERROR = function (msg) {
      //
      // process ERROR reply to SUBSCRIBE
      //
      var request = msg[2];
      var details = msg[3];
      var error = msg[4];

      // optional
      var args = msg[5];
      var kwargs = msg[6];

      if (request in self._subscribe_reqs) {

         var r = self._subscribe_reqs[request];

         var d = r[0];
         var fn = r[1];
         var options = r[2];

         d.reject(error);

         delete self._subscribe_reqs[request];

      } else {
         self._protocol_violation("SUBSCRIBE-ERROR received for non-pending request ID " + request);
      }
   };
   self._MESSAGE_MAP[MSG_TYPE.ERROR][MSG_TYPE.SUBSCRIBE] = self._process_SUBSCRIBE_ERROR;


   self._process_UNSUBSCRIBED = function (msg) {
      //
      // process UNSUBSCRIBED reply to UNSUBSCRIBE
      //
      var request = msg[1];

      if (request in self._unsubscribe_reqs) {

         var r = self._unsubscribe_reqs[request];

         var d = r[0];
         var subscription = r[1];

         if (subscription.id in self._subscriptions) {
            delete self._subscriptions[subscription.id];
         }

         subscription.active = false;
         d.resolve();

         delete self._unsubscribe_reqs[request];

      } else {
         self._protocol_violation("UNSUBSCRIBED received for non-pending request ID " + request);
      }
   };
   self._MESSAGE_MAP[MSG_TYPE.UNSUBSCRIBED] = self._process_UNSUBSCRIBED;


   self._process_UNSUBSCRIBE_ERROR = function (msg) {
      //
      // process ERROR reply to UNSUBSCRIBE
      //
      var request = msg[2];
      var details = msg[3];
      var error = msg[4];

      // optional
      var args = msg[5];
      var kwargs = msg[6];

      if (request in self._unsubscribe_reqs) {

         var r = self._unsubscribe_reqs[request];

         var d = r[0];
         var subscription = r[1];

         d.reject(error);

         delete self._unsubscribe_reqs[request];

      } else {
         self._protocol_violation("UNSUBSCRIBE-ERROR received for non-pending request ID " + request);
      }
   };
   self._MESSAGE_MAP[MSG_TYPE.ERROR][MSG_TYPE.UNSUBSCRIBE] = self._process_UNSUBSCRIBE_ERROR;


   self._process_PUBLISHED = function (msg) {
      //
      // process PUBLISHED reply to PUBLISH
      //
      var request = msg[1];
      var publication = msg[2];

      if (request in self._publish_reqs) {

         var r = self._publish_reqs[request];

         var d = r[0];
         var options = r[1];

         var pub = new Publication(publication);
         d.resolve(pub);

         delete self._publish_reqs[request];

      } else {
         self._protocol_violation("PUBLISHED received for non-pending request ID " + request);
      }
   };
   self._MESSAGE_MAP[MSG_TYPE.PUBLISHED] = self._process_PUBLISHED;


   self._process_PUBLISH_ERROR = function (msg) {
      //
      // process ERROR reply to PUBLISH
      //
      var request = msg[2];
      var details = msg[3];
      var error = msg[4];

      // optional
      var args = msg[5];
      var kwargs = msg[6];

      if (request in self._publish_reqs) {

         var r = self._publish_reqs[request];

         var d = r[0];
         var options = r[1];

         d.reject(error);

         delete self._publish_reqs[request];

      } else {
         self._protocol_violation("PUBLISH-ERROR received for non-pending request ID " + request);
      }
   };
   self._MESSAGE_MAP[MSG_TYPE.ERROR][MSG_TYPE.PUBLISH] = self._process_PUBLISH_ERROR;


   self._process_EVENT = function (msg) {
      //
      // process EVENT message
      //
      // [EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict, PUBLISH.Arguments|list, PUBLISH.ArgumentsKw|dict]

      var subscription = msg[1];

      if (subscription in self._subscriptions) {

         var handler = self._subscriptions[subscription]._handler;

         var publication = msg[2];
         var details = msg[3];

         var args = msg[4] || [];
         var kwargs = msg[5] || {};

         var ed = new Event(publication, details.publisher);

         try {
            handler(args, kwargs, ed);
         } catch (e) {
            console.log("Exception raised in event handler", e);
         }

      } else {
         self._protocol_violation("EVENT received for non-subscribed subscription ID " + subscription);
      }
   };
   self._MESSAGE_MAP[MSG_TYPE.EVENT] = self._process_EVENT;


   self._process_REGISTERED = function (msg) {
      //
      // process REGISTERED reply to REGISTER
      //
      var request = msg[1];
      var registration = msg[2];

      if (request in self._register_reqs) {

         var r = self._register_reqs[request];

         var d = r[0];
         var endpoint = r[1];
         var options = r[2];

         var reg = new Registration(endpoint, self, registration);

         self._registrations[registration] = reg;

         d.resolve(reg);

         delete self._register_reqs[request];

      } else {
         self._protocol_violation("REGISTERED received for non-pending request ID " + request);
      }
   };
   self._MESSAGE_MAP[MSG_TYPE.REGISTERED] = self._process_REGISTERED;


   self._process_REGISTER_ERROR = function (msg) {
      //
      // process ERROR reply to REGISTER
      //
      var request = msg[2];
      var details = msg[3];
      var error = msg[4];

      // optional
      var args = msg[5];
      var kwargs = msg[6];

      if (request in self._register_reqs) {

         var r = self._register_reqs[request];

         var d = r[0];
         var fn = r[1];
         var options = r[2];

         d.reject(error);

         delete self._register_reqs[request];

      } else {
         self._protocol_violation("REGISTER-ERROR received for non-pending request ID " + request);
      }
   };
   self._MESSAGE_MAP[MSG_TYPE.ERROR][MSG_TYPE.REGISTER] = self._process_REGISTER_ERROR;


   self._process_UNREGISTERED = function (msg) {
      //
      // process UNREGISTERED reply to UNREGISTER
      //
      var request = msg[1];

      if (request in self._unregister_reqs) {

         var r = self._unregister_reqs[request];

         var d = r[0];
         var registration = r[1];

         if (registration.id in self._registrations) {
            delete self._registrations[registration.id];
         }

         registration.active = false;
         d.resolve();

         delete self._unregister_reqs[request];

      } else {
         self._protocol_violation("UNREGISTERED received for non-pending request ID " + request);
      }
   };
   self._MESSAGE_MAP[MSG_TYPE.UNREGISTERED] = self._process_UNREGISTERED;


   self._process_UNREGISTER_ERROR = function (msg) {
      //
      // process ERROR reply to UNREGISTER
      //
      var request = msg[2];
      var details = msg[3];
      var error = msg[4];

      // optional
      var args = msg[5];
      var kwargs = msg[6];

      if (request in self._unregister_reqs) {

         var r = self._unregister_reqs[request];

         var d = r[0];
         var registration = r[1];

         d.reject(error);

         delete self._unregister_reqs[request];

      } else {
         self._protocol_violation("UNREGISTER-ERROR received for non-pending request ID " + request);
      }
   };
   self._MESSAGE_MAP[MSG_TYPE.ERROR][MSG_TYPE.UNREGISTER] = self._process_UNREGISTER_ERROR;


   self._process_RESULT = function (msg) {
      //
      // process RESULT reply to CALL
      //
      var request = msg[1];
      if (request in self._call_reqs) {

         var details = msg[2];

         var result = null;
         if (msg.length > 3) {
            if (msg.length > 4 || msg[3].length > 1) {
               // wrap complex result
               result = new Result(msg[3], msg[4]);
            } else {
               // single positional result
               result = msg[3][0];
            }
         }

         var r = self._call_reqs[request];

         var d = r[0];
         var options = r[1];

         if (details.progress) {
            if (options && options.receive_progress) {
               d.notify(result);
            }
         } else {
            d.resolve(result);
            delete self._call_reqs[request];
         }
      } else {
         self._protocol_violation("CALL-RESULT received for non-pending request ID " + request);
      }
   };
   self._MESSAGE_MAP[MSG_TYPE.RESULT] = self._process_RESULT;


   self._process_CALL_ERROR = function (msg) {
      //
      // process ERROR reply to CALL
      //
      var request = msg[2];
      if (request in self._call_reqs) {

         var details = msg[3];
         var error = new Error(msg[4], msg[5], msg[6]);

         var r = self._call_reqs[request];

         var d = r[0];
         var options = r[1];

         d.reject(error);

         delete self._call_reqs[request];

      } else {
         self._protocol_violation("CALL-ERROR received for non-pending request ID " + request);
      }
   };
   self._MESSAGE_MAP[MSG_TYPE.ERROR][MSG_TYPE.CALL] = self._process_CALL_ERROR;


   self._process_INVOCATION = function (msg) {
      //
      // process INVOCATION message
      //
      // [INVOCATION, Request|id, REGISTERED.Registration|id, Details|dict, CALL.Arguments|list, CALL.ArgumentsKw|dict]
      //
      var request = msg[1];
      var registration = msg[2];

      var details = msg[3];
      // receive_progress
      // timeout
      // caller

      if (registration in self._registrations) {

         var endpoint = self._registrations[registration]._endpoint;

         var args = msg[4] || [];
         var kwargs = msg[5] || {};

         // create progress function for invocation
         //
         var progress = null;
         if (details.receive_progress) {

            progress = function (args, kwargs) {
               var progress_msg = [MSG_TYPE.YIELD, request, {progress: true}];

               args = args || [];
               kwargs = kwargs || {};

               var kwargs_len = Object.keys(kwargs).length;
               if (args.length || kwargs_len) {
                  progress_msg.push(args);
                  if (kwargs_len) {
                     progress_msg.push(kwargs);
                  }
               }
               self._send_wamp(progress_msg);
            }
         };

         var cd = new Invocation(details.caller, progress);

         // We use the following whenjs call wrapper, which automatically
         // wraps a plain, non-promise value in a (immediately resolved) promise
         //
         // See: https://github.com/cujojs/when/blob/master/docs/api.md#fncall
         //
         when_fn.call(endpoint, args, kwargs, cd).then(

            function (res) {
               // construct YIELD message
               // FIXME: Options
               //
               var reply = [MSG_TYPE.YIELD, request, {}];

               if (res instanceof Result) {
                  var kwargs_len = Object.keys(res.kwargs).length;
                  if (res.args.length || kwargs_len) {
                     reply.push(res.args);
                     if (kwargs_len) {
                        reply.push(res.kwargs);
                     }
                  }
               } else {
                  reply.push([res]);
               }

               // send WAMP message
               //
               self._send_wamp(reply);
            },

            function (err) {
               // construct ERROR message
               // [ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri, Arguments|list, ArgumentsKw|dict]

               var reply = [MSG_TYPE.ERROR, MSG_TYPE.INVOCATION, request, {}];

               if (err instanceof Error) {

                  reply.push(err.error);

                  var kwargs_len = Object.keys(err.kwargs).length;
                  if (err.args.length || kwargs_len) {
                     reply.push(err.args);
                     if (kwargs_len) {
                        reply.push(err.kwargs);
                     }
                  }
               } else {
                  reply.push('wamp.error.runtime_error');
                  reply.push([err]);
               }

               // send WAMP message
               //
               self._send_wamp(reply);
            }
         );

      } else {
         self._protocol_violation("INVOCATION received for non-registered registration ID " + request);
      }
   };
   self._MESSAGE_MAP[MSG_TYPE.INVOCATION] = self._process_INVOCATION;


   self._socket.onmessage = function (evt) {

      var msg = JSON.parse(evt.data);
      var msg_type = msg[0];

      // WAMP session not yet open
      //
      if (!self.id) {

         // the first message must be WELCOME, ABORT or CHALLENGE ..
         //
         if (msg_type === MSG_TYPE.WELCOME) {

            self.id = msg[1];

            // determine actual set of advanced features that can be used
            //
            var rf = msg[2];
            self._features = {};

            if (rf.roles.broker) {
               // "Basic Profile" is mandatory
               self._features.subscriber = {};
               self._features.publisher = {};

               // fill in features that both peers support
               if (rf.roles.broker.features) {

                  for (var att in WAMP_FEATURES.roles.publisher.features) {
                     self._features.publisher[att] = WAMP_FEATURES.roles.publisher.features[att] &&
                                                     rf.roles.broker.features[att];
                  }

                  for (var att in WAMP_FEATURES.roles.subscriber.features) {
                     self._features.subscriber[att] = WAMP_FEATURES.roles.subscriber.features[att] &&
                                                      rf.roles.broker.features[att];
                  }
               }
            }

            if (rf.roles.dealer) {
               // "Basic Profile" is mandatory
               self._features.caller = {};
               self._features.callee = {};

               // fill in features that both peers support
               if (rf.roles.dealer.features) {

                  for (var att in WAMP_FEATURES.roles.caller.features) {
                     self._features.caller[att] = WAMP_FEATURES.roles.caller.features[att] &&
                                                  rf.roles.dealer.features[att];
                  }

                  for (var att in WAMP_FEATURES.roles.callee.features) {
                     self._features.callee[att] = WAMP_FEATURES.roles.callee.features[att] &&
                                                  rf.roles.dealer.features[att];
                  }
               }
            }

            if (self.onjoin) {
               self.onjoin(msg[2]);
            }

         } else if (msg_type === MSG_TYPE.ABORT) {

            // FIXME
            console.log("Unhandled ABORT message", msg);

         } else if (msg_type === MSG_TYPE.CHALLENGE) {

            if (self._options.onchallenge) {

               var method = msg[1];
               var extra = msg[2];

               when_fn.call(self._options.onchallenge, self, method, extra).then(
                  function (signature) {
                     var msg = [MSG_TYPE.AUTHENTICATE, signature, {}];
                     self._send_wamp(msg);
                  },
                  function (err) {
                     console.log("onchallenge() raised:", err);
                  }
               );
            } else {
               console.log("received WAMP challenge, but no onchallenge() handler set");
            }

         } else {
            self._protocol_violation("unexpected message type " + msg_type);
         }

      // WAMP session is open
      //
      } else {

         if (msg_type === MSG_TYPE.GOODBYE) {

            if (!self._goodbye_sent) {

               var reply = [MSG_TYPE.GOODBYE, {}, "wamp.error.goodbye_and_out"];
               self._send_wamp(reply);
            }

            self.id = null;
            self.realm = null;
            self._features = null;

            if (self.onleave) {
               self.onleave();
            }

         } else {

            if (msg_type === MSG_TYPE.ERROR) {

               var request_type = msg[1];
               if (request_type in self._MESSAGE_MAP[MSG_TYPE.ERROR]) {

                  self._MESSAGE_MAP[msg_type][request_type](msg);

               } else {

                  self._protocol_violation("unexpected ERROR message with request_type " + request_type);
               }

            } else {

               if (msg_type in self._MESSAGE_MAP) {

                  self._MESSAGE_MAP[msg_type](msg);

               } else {

                  self._protocol_violation("unexpected message type " + msg_type);
               }
            }
         }
      }
   };
};


Object.defineProperty(Session.prototype, "isOpen", {
   get: function () {
      return this.id !== null;
   }
});


Object.defineProperty(Session.prototype, "features", {
   get: function () {
      return this._features;
   }
});


Object.defineProperty(Session.prototype, "subscriptions", {
   get: function () {
      var keys = Object.keys(this._subscriptions);
      var vals = [];
      for (var i = 0; i < keys.length; ++i) {
         vals.push(this._subscriptions[keys[i]]);
      }
      return vals;
   }
});


Object.defineProperty(Session.prototype, "registrations", {
   get: function () {
      var keys = Object.keys(this._registrations);
      var vals = [];
      for (var i = 0; i < keys.length; ++i) {
         vals.push(this._registrations[keys[i]]);
      }
      return vals;
   }
});


Session.prototype.join = function (realm) {

   var self = this;

   if (self.id) {
      throw "session already established";
   }

   self._goodbye_sent = false;
   self.realm = realm;

   var msg = [MSG_TYPE.HELLO, realm, WAMP_FEATURES];
   self._send_wamp(msg);
};


Session.prototype.leave = function (reason, message) {

   var self = this;

   if (!self.id) {
      throw "no session currently established";
   }

   if (!reason) {
      reason = "wamp.close.normal";
   }

   var details = {};
   if (message) {
      details.message = message;
   }

   var msg = [MSG_TYPE.GOODBYE, details, reason];
   self._send_wamp(msg);
   self._goodbye_sent = true;
};


Session.prototype.call = function (procedure, pargs, kwargs, options) {
   var self = this;

   // create and remember new CALL request
   //
   var request = newid();
   var d = self.defer();
   self._call_reqs[request] = [d, options];

   // construct CALL message
   //
   var msg = [MSG_TYPE.CALL, request];
   msg.push(options || {})
   msg.push(procedure);
   if (pargs) {
      msg.push(pargs);
      if (kwargs) {
         msg.push(kwargs);
      }
   }

   // send WAMP message
   //
   self._send_wamp(msg);

   return d.promise;
};


// old WAMP call
Session.prototype.call1 = function () {

   var self = this;
   var procedure = arguments[0];

   var pargs = [];
   for (var i = 1; i < arguments.length; i += 1) {
      pargs.push(arguments[i]);
   }

   return self.xcall(procedure, pargs);
};


Session.prototype.publish = function (topic, pargs, kwargs, options) {
   var self = this;

   var ack = options && options.acknowledge;
   var d = null;

   // create and remember new PUBLISH request
   //
   var request = newid();
   if (ack) {
      d = self.defer();
      self._publish_reqs[request] = [d, options];
   }

   // construct PUBLISH message
   //
   var msg = [MSG_TYPE.PUBLISH, request];
   if (options) {
      msg.push(options);
   } else {
      msg.push({});
   }
   msg.push(topic);
   if (pargs) {
      msg.push(pargs);
      if (kwargs) {
         msg.push(kwargs);
      }
   }

   // send WAMP message
   //
   self._send_wamp(msg);

   if (d) {
      return d.promise;
   }
};


// old WAMP publish
Session.prototype.publish1 = function (topic, payload, options) {
   return this.publish(topic, [payload], {}, options);
};


Session.prototype.subscribe = function (topic, handler, options) {
   var self = this;

   // create an remember new SUBSCRIBE request
   //
   var request = newid();
   var d = self.defer();
   self._subscribe_reqs[request] = [d, handler, options];

   // construct SUBSCRIBE message
   //
   var msg = [MSG_TYPE.SUBSCRIBE, request];
   if (options) {
      msg.push(options);
   } else {
      msg.push({});
   }
   msg.push(topic);

   // send WAMP message
   //
   self._send_wamp(msg);

   return d.promise;
};


Session.prototype.register = function (procedure, endpoint, options) {
   var self = this;

   // create an remember new REGISTER request
   //
   var request = newid();
   var d = self.defer();
   self._register_reqs[request] = [d, endpoint, options];

   // construct REGISTER message
   //
   var msg = [MSG_TYPE.REGISTER, request];
   if (options) {
      msg.push(options);
   } else {
      msg.push({});
   }
   msg.push(procedure);

   // send WAMP message
   //
   self._send_wamp(msg);

   return d.promise;
};


Session.prototype._unsubscribe = function (subscription) {
   var self = this;

   if (!subscription.active || !(subscription.id in self._subscriptions)) {
      throw "subscription not active";
   }

   // create and remember new UNSUBSCRIBE request
   //
   var request = newid();
   var d = self.defer();
   self._unsubscribe_reqs[request] = [d, subscription];

   // construct UNSUBSCRIBE message
   //
   var msg = [MSG_TYPE.UNSUBSCRIBE, request, subscription.id];

   // send WAMP message
   //
   self._send_wamp(msg);

   return d.promise;
};


Session.prototype._unregister = function (registration) {
   var self = this;

   if (!registration.active || !(registration.id in self._registrations)) {
      throw "registration not active";
   }

   // create and remember new UNREGISTER request
   //
   var request = newid();
   var d = self.defer();
   self._unregister_reqs[request] = [d, registration];

   // construct UNREGISTER message
   //
   var msg = [MSG_TYPE.UNREGISTER, request, registration.id];

   // send WAMP message
   //
   self._send_wamp(msg);

   return d.promise;
};


exports.Session = Session;

exports.Invocation = Invocation;
exports.Event = Event;
exports.Result = Result;
exports.Error = Error;
exports.Subscription = Subscription;
exports.Registration = Registration;
exports.Publication = Publication;

},{"./websocket.js":6,"crypto-js":15,"when":42,"when/function":41}],6:[function(require,module,exports){
var global=self;///////////////////////////////////////////////////////////////////////////////
//
//  AutobahnJS - http://autobahn.ws, http://wamp.ws
//
//  A JavaScript library for WAMP ("The Web Application Messaging Protocol").
//
//  Copyright (C) 2011-2014 Tavendo GmbH, http://tavendo.com
//
//  Licensed under the MIT License.
//  http://www.opensource.org/licenses/mit-license.php
//
///////////////////////////////////////////////////////////////////////////////


var RawWebSocket = function (url, protocols) {

   if ('window' in global) {

      //
      // running in browser
      //

      if ("WebSocket" in window) {
         // Chrome, MSIE, newer Firefox
         if (protocols) {
            return new window.WebSocket(url, protocols);
         } else {
            return new window.WebSocket(url);
         }
      } else if ("MozWebSocket" in window) {
         // older versions of Firefox prefix the WebSocket object
         if (protocols) {
            return new window.MozWebSocket(url, protocols);
         } else {
            return new window.MozWebSocket(url);
         }
      } else {
         return null;
      }

   } else {

      //
      // running on nodejs
      //

      // our WebSocket shim with W3C API
      var websocket = {};

      // these will get defined by the specific shim
      websocket.protocol = undefined;
      websocket.send = undefined;
      websocket.close = undefined;

      // these will get called by the shim.
      // in case user code doesn't override these, provide these NOPs
      websocket.onmessage = function () {};
      websocket.onopen = function () {};
      websocket.onclose = function () {};

      // https://github.com/Worlize/WebSocket-Node
      //
/*      
      (function() {

         //var WebSocketClient = require('websocket').client;
         var client = new WebSocketClient();

         client.on('connectFailed', function (error) {
            // https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent
            websocket.onclose({code: 1000, reason: error.toString(), wasClean: false});
         });

         client.on('connect', function (connection) {

            websocket.protocol = connection.protocol;

            websocket.send = function (msg) {
               if (connection.connected) {
                  // sending a string that gets encoded as UTF8
                  // https://github.com/Worlize/WebSocket-Node/blob/master/lib/WebSocketConnection.js#L587
                  connection.sendUTF(msg);

                  // https://github.com/Worlize/WebSocket-Node/blob/master/lib/WebSocketConnection.js#L594
                  // sending a Node Buffer
                  //connection.sendBytes(msg);
               }
            };

            websocket.close = function (code, reason) {
               connection.close();
            };

            websocket.onopen();
       
            connection.on('error', function (error) {
               // https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent
               websocket.onclose({code: 1000, reason: error.toString(), wasClean: true});
            });

            connection.on('close', function (code, reason) {
               // https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent
               websocket.onclose({code: code, reason: reason, wasClean: true});
            });

            connection.on('message', function (message) {
               // https://developer.mozilla.org/en-US/docs/Web/API/MessageEvent
               if (message.type === 'utf8') {
                  websocket.onmessage({data: message.utf8Data});
               }
            });

         });

         if (protocols) {
            client.connect(url, protocols);
         } else {
            client.connect(url);
         }
      })();
*/

      // https://github.com/einaros/ws
      //
      (function () {

         var WebSocket = require('ws');
         var client;
         if (protocols) {
            if (Array.isArray(protocols)) {
               protocols = protocols.join(',');
            }
            client = new WebSocket(url, {protocol: protocols});
         } else {
            client = new WebSocket(url);
         }

         websocket.send = function (msg) {
            client.send(msg, {binary: false});
         };

         websocket.close = function (code, reason) {
            client.close();
         };

         client.on('open', function () {
            websocket.onopen();
         });

         client.on('message', function (data, flags) {
            if (flags.binary) {

            } else {
               websocket.onmessage({data: data});
            }
         });

         client.on('close', function () {
         });

         client.on('error', function () {
         });

      })();

      return websocket;
   }
};


var _WebSocket = function (url, options) {
   var self = this;
   self._url = url;
   self._options = options;
};


_WebSocket.prototype.create = function () {
   var self = this;
   return new RawWebSocket(self._url, ['wamp.2.json']);
};

exports.WebSocket = _WebSocket;

},{"ws":43}],7:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./enc-base64"),require("./md5"),require("./evpkdf"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./enc-base64","./md5","./evpkdf","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return function(){var r=e,t=r.lib,i=t.BlockCipher,o=r.algo,n=[],c=[],s=[],a=[],f=[],u=[],h=[],p=[],d=[],l=[];(function(){for(var e=[],r=0;256>r;r++)e[r]=128>r?r<<1:283^r<<1;for(var t=0,i=0,r=0;256>r;r++){var o=i^i<<1^i<<2^i<<3^i<<4;o=99^(o>>>8^255&o),n[t]=o,c[o]=t;var y=e[t],v=e[y],m=e[v],x=257*e[o]^16843008*o;s[t]=x<<24|x>>>8,a[t]=x<<16|x>>>16,f[t]=x<<8|x>>>24,u[t]=x;var x=16843009*m^65537*v^257*y^16843008*t;h[o]=x<<24|x>>>8,p[o]=x<<16|x>>>16,d[o]=x<<8|x>>>24,l[o]=x,t?(t=y^e[e[e[m^y]]],i^=e[e[i]]):t=i=1}})();var y=[0,1,2,4,8,16,32,64,128,27,54],v=o.AES=i.extend({_doReset:function(){for(var e=this._key,r=e.words,t=e.sigBytes/4,i=this._nRounds=t+6,o=4*(i+1),c=this._keySchedule=[],s=0;o>s;s++)if(t>s)c[s]=r[s];else{var a=c[s-1];s%t?t>6&&4==s%t&&(a=n[a>>>24]<<24|n[255&a>>>16]<<16|n[255&a>>>8]<<8|n[255&a]):(a=a<<8|a>>>24,a=n[a>>>24]<<24|n[255&a>>>16]<<16|n[255&a>>>8]<<8|n[255&a],a^=y[0|s/t]<<24),c[s]=c[s-t]^a}for(var f=this._invKeySchedule=[],u=0;o>u;u++){var s=o-u;if(u%4)var a=c[s];else var a=c[s-4];f[u]=4>u||4>=s?a:h[n[a>>>24]]^p[n[255&a>>>16]]^d[n[255&a>>>8]]^l[n[255&a]]}},encryptBlock:function(e,r){this._doCryptBlock(e,r,this._keySchedule,s,a,f,u,n)},decryptBlock:function(e,r){var t=e[r+1];e[r+1]=e[r+3],e[r+3]=t,this._doCryptBlock(e,r,this._invKeySchedule,h,p,d,l,c);var t=e[r+1];e[r+1]=e[r+3],e[r+3]=t},_doCryptBlock:function(e,r,t,i,o,n,c,s){for(var a=this._nRounds,f=e[r]^t[0],u=e[r+1]^t[1],h=e[r+2]^t[2],p=e[r+3]^t[3],d=4,l=1;a>l;l++){var y=i[f>>>24]^o[255&u>>>16]^n[255&h>>>8]^c[255&p]^t[d++],v=i[u>>>24]^o[255&h>>>16]^n[255&p>>>8]^c[255&f]^t[d++],m=i[h>>>24]^o[255&p>>>16]^n[255&f>>>8]^c[255&u]^t[d++],x=i[p>>>24]^o[255&f>>>16]^n[255&u>>>8]^c[255&h]^t[d++];f=y,u=v,h=m,p=x}var y=(s[f>>>24]<<24|s[255&u>>>16]<<16|s[255&h>>>8]<<8|s[255&p])^t[d++],v=(s[u>>>24]<<24|s[255&h>>>16]<<16|s[255&p>>>8]<<8|s[255&f])^t[d++],m=(s[h>>>24]<<24|s[255&p>>>16]<<16|s[255&f>>>8]<<8|s[255&u])^t[d++],x=(s[p>>>24]<<24|s[255&f>>>16]<<16|s[255&u>>>8]<<8|s[255&h])^t[d++];e[r]=y,e[r+1]=v,e[r+2]=m,e[r+3]=x},keySize:8});r.AES=i._createHelper(v)}(),e.AES});
},{"./cipher-core":8,"./core":9,"./enc-base64":10,"./evpkdf":12,"./md5":17}],8:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core")):"function"==typeof define&&define.amd?define(["./core"],r):r(e.CryptoJS)})(this,function(e){e.lib.Cipher||function(r){var t=e,i=t.lib,n=i.Base,o=i.WordArray,c=i.BufferedBlockAlgorithm,s=t.enc;s.Utf8;var a=s.Base64,f=t.algo,u=f.EvpKDF,h=i.Cipher=c.extend({cfg:n.extend(),createEncryptor:function(e,r){return this.create(this._ENC_XFORM_MODE,e,r)},createDecryptor:function(e,r){return this.create(this._DEC_XFORM_MODE,e,r)},init:function(e,r,t){this.cfg=this.cfg.extend(t),this._xformMode=e,this._key=r,this.reset()},reset:function(){c.reset.call(this),this._doReset()},process:function(e){return this._append(e),this._process()},finalize:function(e){e&&this._append(e);var r=this._doFinalize();return r},keySize:4,ivSize:4,_ENC_XFORM_MODE:1,_DEC_XFORM_MODE:2,_createHelper:function(){function e(e){return"string"==typeof e?B:_}return function(r){return{encrypt:function(t,i,n){return e(i).encrypt(r,t,i,n)},decrypt:function(t,i,n){return e(i).decrypt(r,t,i,n)}}}}()});i.StreamCipher=h.extend({_doFinalize:function(){var e=this._process(true);return e},blockSize:1});var d=t.mode={},p=i.BlockCipherMode=n.extend({createEncryptor:function(e,r){return this.Encryptor.create(e,r)},createDecryptor:function(e,r){return this.Decryptor.create(e,r)},init:function(e,r){this._cipher=e,this._iv=r}}),l=d.CBC=function(){function e(e,t,i){var n=this._iv;if(n){var o=n;this._iv=r}else var o=this._prevBlock;for(var c=0;i>c;c++)e[t+c]^=o[c]}var t=p.extend();return t.Encryptor=t.extend({processBlock:function(r,t){var i=this._cipher,n=i.blockSize;e.call(this,r,t,n),i.encryptBlock(r,t),this._prevBlock=r.slice(t,t+n)}}),t.Decryptor=t.extend({processBlock:function(r,t){var i=this._cipher,n=i.blockSize,o=r.slice(t,t+n);i.decryptBlock(r,t),e.call(this,r,t,n),this._prevBlock=o}}),t}(),y=t.pad={},v=y.Pkcs7={pad:function(e,r){for(var t=4*r,i=t-e.sigBytes%t,n=i<<24|i<<16|i<<8|i,c=[],s=0;i>s;s+=4)c.push(n);var a=o.create(c,i);e.concat(a)},unpad:function(e){var r=255&e.words[e.sigBytes-1>>>2];e.sigBytes-=r}};i.BlockCipher=h.extend({cfg:h.cfg.extend({mode:l,padding:v}),reset:function(){h.reset.call(this);var e=this.cfg,r=e.iv,t=e.mode;if(this._xformMode==this._ENC_XFORM_MODE)var i=t.createEncryptor;else{var i=t.createDecryptor;this._minBufferSize=1}this._mode=i.call(t,this,r&&r.words)},_doProcessBlock:function(e,r){this._mode.processBlock(e,r)},_doFinalize:function(){var e=this.cfg.padding;if(this._xformMode==this._ENC_XFORM_MODE){e.pad(this._data,this.blockSize);var r=this._process(true)}else{var r=this._process(true);e.unpad(r)}return r},blockSize:4});var m=i.CipherParams=n.extend({init:function(e){this.mixIn(e)},toString:function(e){return(e||this.formatter).stringify(this)}}),g=t.format={},x=g.OpenSSL={stringify:function(e){var r=e.ciphertext,t=e.salt;if(t)var i=o.create([1398893684,1701076831]).concat(t).concat(r);else var i=r;return i.toString(a)},parse:function(e){var r=a.parse(e),t=r.words;if(1398893684==t[0]&&1701076831==t[1]){var i=o.create(t.slice(2,4));t.splice(0,4),r.sigBytes-=16}return m.create({ciphertext:r,salt:i})}},_=i.SerializableCipher=n.extend({cfg:n.extend({format:x}),encrypt:function(e,r,t,i){i=this.cfg.extend(i);var n=e.createEncryptor(t,i),o=n.finalize(r),c=n.cfg;return m.create({ciphertext:o,key:t,iv:c.iv,algorithm:e,mode:c.mode,padding:c.padding,blockSize:e.blockSize,formatter:i.format})},decrypt:function(e,r,t,i){i=this.cfg.extend(i),r=this._parse(r,i.format);var n=e.createDecryptor(t,i).finalize(r.ciphertext);return n},_parse:function(e,r){return"string"==typeof e?r.parse(e,this):e}}),w=t.kdf={},S=w.OpenSSL={execute:function(e,r,t,i){i||(i=o.random(8));var n=u.create({keySize:r+t}).compute(e,i),c=o.create(n.words.slice(r),4*t);return n.sigBytes=4*r,m.create({key:n,iv:c,salt:i})}},B=i.PasswordBasedCipher=_.extend({cfg:_.cfg.extend({kdf:S}),encrypt:function(e,r,t,i){i=this.cfg.extend(i);var n=i.kdf.execute(t,e.keySize,e.ivSize);i.iv=n.iv;var o=_.encrypt.call(this,e,r,n.key,i);return o.mixIn(n),o},decrypt:function(e,r,t,i){i=this.cfg.extend(i),r=this._parse(r,i.format);var n=i.kdf.execute(t,e.keySize,e.ivSize,r.salt);i.iv=n.iv;var o=_.decrypt.call(this,e,r,n.key,i);return o}})}()});
},{"./core":9}],9:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r():"function"==typeof define&&define.amd?define([],r):e.CryptoJS=r()})(this,function(){var e=e||function(e,r){var t={},i=t.lib={},n=i.Base=function(){function e(){}return{extend:function(r){e.prototype=this;var t=new e;return r&&t.mixIn(r),t.hasOwnProperty("init")||(t.init=function(){t.$super.init.apply(this,arguments)}),t.init.prototype=t,t.$super=this,t},create:function(){var e=this.extend();return e.init.apply(e,arguments),e},init:function(){},mixIn:function(e){for(var r in e)e.hasOwnProperty(r)&&(this[r]=e[r]);e.hasOwnProperty("toString")&&(this.toString=e.toString)},clone:function(){return this.init.prototype.extend(this)}}}(),o=i.WordArray=n.extend({init:function(e,t){e=this.words=e||[],this.sigBytes=t!=r?t:4*e.length},toString:function(e){return(e||s).stringify(this)},concat:function(e){var r=this.words,t=e.words,i=this.sigBytes,n=e.sigBytes;if(this.clamp(),i%4)for(var o=0;n>o;o++){var c=255&t[o>>>2]>>>24-8*(o%4);r[i+o>>>2]|=c<<24-8*((i+o)%4)}else if(t.length>65535)for(var o=0;n>o;o+=4)r[i+o>>>2]=t[o>>>2];else r.push.apply(r,t);return this.sigBytes+=n,this},clamp:function(){var r=this.words,t=this.sigBytes;r[t>>>2]&=4294967295<<32-8*(t%4),r.length=e.ceil(t/4)},clone:function(){var e=n.clone.call(this);return e.words=this.words.slice(0),e},random:function(r){for(var t=[],i=0;r>i;i+=4)t.push(0|4294967296*e.random());return new o.init(t,r)}}),c=t.enc={},s=c.Hex={stringify:function(e){for(var r=e.words,t=e.sigBytes,i=[],n=0;t>n;n++){var o=255&r[n>>>2]>>>24-8*(n%4);i.push((o>>>4).toString(16)),i.push((15&o).toString(16))}return i.join("")},parse:function(e){for(var r=e.length,t=[],i=0;r>i;i+=2)t[i>>>3]|=parseInt(e.substr(i,2),16)<<24-4*(i%8);return new o.init(t,r/2)}},u=c.Latin1={stringify:function(e){for(var r=e.words,t=e.sigBytes,i=[],n=0;t>n;n++){var o=255&r[n>>>2]>>>24-8*(n%4);i.push(String.fromCharCode(o))}return i.join("")},parse:function(e){for(var r=e.length,t=[],i=0;r>i;i++)t[i>>>2]|=(255&e.charCodeAt(i))<<24-8*(i%4);return new o.init(t,r)}},f=c.Utf8={stringify:function(e){try{return decodeURIComponent(escape(u.stringify(e)))}catch(r){throw Error("Malformed UTF-8 data")}},parse:function(e){return u.parse(unescape(encodeURIComponent(e)))}},a=i.BufferedBlockAlgorithm=n.extend({reset:function(){this._data=new o.init,this._nDataBytes=0},_append:function(e){"string"==typeof e&&(e=f.parse(e)),this._data.concat(e),this._nDataBytes+=e.sigBytes},_process:function(r){var t=this._data,i=t.words,n=t.sigBytes,c=this.blockSize,s=4*c,u=n/s;u=r?e.ceil(u):e.max((0|u)-this._minBufferSize,0);var f=u*c,a=e.min(4*f,n);if(f){for(var p=0;f>p;p+=c)this._doProcessBlock(i,p);var d=i.splice(0,f);t.sigBytes-=a}return new o.init(d,a)},clone:function(){var e=n.clone.call(this);return e._data=this._data.clone(),e},_minBufferSize:0});i.Hasher=a.extend({cfg:n.extend(),init:function(e){this.cfg=this.cfg.extend(e),this.reset()},reset:function(){a.reset.call(this),this._doReset()},update:function(e){return this._append(e),this._process(),this},finalize:function(e){e&&this._append(e);var r=this._doFinalize();return r},blockSize:16,_createHelper:function(e){return function(r,t){return new e.init(t).finalize(r)}},_createHmacHelper:function(e){return function(r,t){return new p.HMAC.init(e,t).finalize(r)}}});var p=t.algo={};return t}(Math);return e});
},{}],10:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core")):"function"==typeof define&&define.amd?define(["./core"],r):r(e.CryptoJS)})(this,function(e){return function(){var r=e,t=r.lib,n=t.WordArray,i=r.enc;i.Base64={stringify:function(e){var r=e.words,t=e.sigBytes,n=this._map;e.clamp();for(var i=[],o=0;t>o;o+=3)for(var s=255&r[o>>>2]>>>24-8*(o%4),c=255&r[o+1>>>2]>>>24-8*((o+1)%4),a=255&r[o+2>>>2]>>>24-8*((o+2)%4),f=s<<16|c<<8|a,u=0;4>u&&t>o+.75*u;u++)i.push(n.charAt(63&f>>>6*(3-u)));var d=n.charAt(64);if(d)for(;i.length%4;)i.push(d);return i.join("")},parse:function(e){var r=e.length,t=this._map,i=t.charAt(64);if(i){var o=e.indexOf(i);-1!=o&&(r=o)}for(var s=[],c=0,a=0;r>a;a++)if(a%4){var f=t.indexOf(e.charAt(a-1))<<2*(a%4),u=t.indexOf(e.charAt(a))>>>6-2*(a%4);s[c>>>2]|=(f|u)<<24-8*(c%4),c++}return n.create(s,c)},_map:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="}}(),e.enc.Base64});
},{"./core":9}],11:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core")):"function"==typeof define&&define.amd?define(["./core"],r):r(e.CryptoJS)})(this,function(e){return function(){function r(e){return 4278255360&e<<8|16711935&e>>>8}var t=e,n=t.lib,i=n.WordArray,o=t.enc;o.Utf16=o.Utf16BE={stringify:function(e){for(var r=e.words,t=e.sigBytes,n=[],i=0;t>i;i+=2){var o=65535&r[i>>>2]>>>16-8*(i%4);n.push(String.fromCharCode(o))}return n.join("")},parse:function(e){for(var r=e.length,t=[],n=0;r>n;n++)t[n>>>1]|=e.charCodeAt(n)<<16-16*(n%2);return i.create(t,2*r)}},o.Utf16LE={stringify:function(e){for(var t=e.words,n=e.sigBytes,i=[],o=0;n>o;o+=2){var c=r(65535&t[o>>>2]>>>16-8*(o%4));i.push(String.fromCharCode(c))}return i.join("")},parse:function(e){for(var t=e.length,n=[],o=0;t>o;o++)n[o>>>1]|=r(e.charCodeAt(o)<<16-16*(o%2));return i.create(n,2*t)}}}(),e.enc.Utf16});
},{"./core":9}],12:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./sha1"),require("./hmac")):"function"==typeof define&&define.amd?define(["./core","./sha1","./hmac"],r):r(e.CryptoJS)})(this,function(e){return function(){var r=e,t=r.lib,i=t.Base,n=t.WordArray,o=r.algo,s=o.MD5,a=o.EvpKDF=i.extend({cfg:i.extend({keySize:4,hasher:s,iterations:1}),init:function(e){this.cfg=this.cfg.extend(e)},compute:function(e,r){for(var t=this.cfg,i=t.hasher.create(),o=n.create(),s=o.words,a=t.keySize,c=t.iterations;a>s.length;){f&&i.update(f);var f=i.update(e).finalize(r);i.reset();for(var u=1;c>u;u++)f=i.finalize(f),i.reset();o.concat(f)}return o.sigBytes=4*a,o}});r.EvpKDF=function(e,r,t){return a.create(t).compute(e,r)}}(),e.EvpKDF});
},{"./core":9,"./hmac":14,"./sha1":33}],13:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return function(){var r=e,t=r.lib,i=t.CipherParams,o=r.enc,n=o.Hex,c=r.format;c.Hex={stringify:function(e){return e.ciphertext.toString(n)},parse:function(e){var r=n.parse(e);return i.create({ciphertext:r})}}}(),e.format.Hex});
},{"./cipher-core":8,"./core":9}],14:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core")):"function"==typeof define&&define.amd?define(["./core"],r):r(e.CryptoJS)})(this,function(e){(function(){var r=e,t=r.lib,n=t.Base,i=r.enc,o=i.Utf8,s=r.algo;s.HMAC=n.extend({init:function(e,r){e=this._hasher=new e.init,"string"==typeof r&&(r=o.parse(r));var t=e.blockSize,n=4*t;r.sigBytes>n&&(r=e.finalize(r)),r.clamp();for(var i=this._oKey=r.clone(),s=this._iKey=r.clone(),a=i.words,c=s.words,f=0;t>f;f++)a[f]^=1549556828,c[f]^=909522486;i.sigBytes=s.sigBytes=n,this.reset()},reset:function(){var e=this._hasher;e.reset(),e.update(this._iKey)},update:function(e){return this._hasher.update(e),this},finalize:function(e){var r=this._hasher,t=r.finalize(e);r.reset();var n=r.finalize(this._oKey.clone().concat(t));return n}})})()});
},{"./core":9}],15:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./x64-core"),require("./lib-typedarrays"),require("./enc-utf16"),require("./enc-base64"),require("./md5"),require("./sha1"),require("./sha256"),require("./sha224"),require("./sha512"),require("./sha384"),require("./sha3"),require("./ripemd160"),require("./hmac"),require("./pbkdf2"),require("./evpkdf"),require("./cipher-core"),require("./mode-cfb"),require("./mode-ctr"),require("./mode-ctr-gladman"),require("./mode-ofb"),require("./mode-ecb"),require("./pad-ansix923"),require("./pad-iso10126"),require("./pad-iso97971"),require("./pad-zeropadding"),require("./pad-nopadding"),require("./format-hex"),require("./aes"),require("./tripledes"),require("./rc4"),require("./rabbit"),require("./rabbit-legacy")):"function"==typeof define&&define.amd?define(["./core","./x64-core","./lib-typedarrays","./enc-utf16","./enc-base64","./md5","./sha1","./sha256","./sha224","./sha512","./sha384","./sha3","./ripemd160","./hmac","./pbkdf2","./evpkdf","./cipher-core","./mode-cfb","./mode-ctr","./mode-ctr-gladman","./mode-ofb","./mode-ecb","./pad-ansix923","./pad-iso10126","./pad-iso97971","./pad-zeropadding","./pad-nopadding","./format-hex","./aes","./tripledes","./rc4","./rabbit","./rabbit-legacy"],r):r(e.CryptoJS)})(this,function(e){return e});
},{"./aes":7,"./cipher-core":8,"./core":9,"./enc-base64":10,"./enc-utf16":11,"./evpkdf":12,"./format-hex":13,"./hmac":14,"./lib-typedarrays":16,"./md5":17,"./mode-cfb":18,"./mode-ctr":20,"./mode-ctr-gladman":19,"./mode-ecb":21,"./mode-ofb":22,"./pad-ansix923":23,"./pad-iso10126":24,"./pad-iso97971":25,"./pad-nopadding":26,"./pad-zeropadding":27,"./pbkdf2":28,"./rabbit":30,"./rabbit-legacy":29,"./rc4":31,"./ripemd160":32,"./sha1":33,"./sha224":34,"./sha256":35,"./sha3":36,"./sha384":37,"./sha512":38,"./tripledes":39,"./x64-core":40}],16:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core")):"function"==typeof define&&define.amd?define(["./core"],r):r(e.CryptoJS)})(this,function(e){return function(){if("function"==typeof ArrayBuffer){var r=e,t=r.lib,i=t.WordArray,n=i.init,o=i.init=function(e){if(e instanceof ArrayBuffer&&(e=new Uint8Array(e)),(e instanceof Int8Array||e instanceof Uint8ClampedArray||e instanceof Int16Array||e instanceof Uint16Array||e instanceof Int32Array||e instanceof Uint32Array||e instanceof Float32Array||e instanceof Float64Array)&&(e=new Uint8Array(e.buffer,e.byteOffset,e.byteLength)),e instanceof Uint8Array){for(var r=e.byteLength,t=[],i=0;r>i;i++)t[i>>>2]|=e[i]<<24-8*(i%4);n.call(this,t,r)}else n.apply(this,arguments)};o.prototype=i}}(),e.lib.WordArray});
},{"./core":9}],17:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core")):"function"==typeof define&&define.amd?define(["./core"],r):r(e.CryptoJS)})(this,function(e){return function(r){function t(e,r,t,n,i,o,s){var c=e+(r&t|~r&n)+i+s;return(c<<o|c>>>32-o)+r}function n(e,r,t,n,i,o,s){var c=e+(r&n|t&~n)+i+s;return(c<<o|c>>>32-o)+r}function i(e,r,t,n,i,o,s){var c=e+(r^t^n)+i+s;return(c<<o|c>>>32-o)+r}function o(e,r,t,n,i,o,s){var c=e+(t^(r|~n))+i+s;return(c<<o|c>>>32-o)+r}var s=e,c=s.lib,f=c.WordArray,a=c.Hasher,u=s.algo,p=[];(function(){for(var e=0;64>e;e++)p[e]=0|4294967296*r.abs(r.sin(e+1))})();var d=u.MD5=a.extend({_doReset:function(){this._hash=new f.init([1732584193,4023233417,2562383102,271733878])},_doProcessBlock:function(e,r){for(var s=0;16>s;s++){var c=r+s,f=e[c];e[c]=16711935&(f<<8|f>>>24)|4278255360&(f<<24|f>>>8)}var a=this._hash.words,u=e[r+0],d=e[r+1],h=e[r+2],y=e[r+3],m=e[r+4],l=e[r+5],x=e[r+6],q=e[r+7],g=e[r+8],v=e[r+9],b=e[r+10],S=e[r+11],w=e[r+12],C=e[r+13],_=e[r+14],A=e[r+15],B=a[0],H=a[1],j=a[2],J=a[3];B=t(B,H,j,J,u,7,p[0]),J=t(J,B,H,j,d,12,p[1]),j=t(j,J,B,H,h,17,p[2]),H=t(H,j,J,B,y,22,p[3]),B=t(B,H,j,J,m,7,p[4]),J=t(J,B,H,j,l,12,p[5]),j=t(j,J,B,H,x,17,p[6]),H=t(H,j,J,B,q,22,p[7]),B=t(B,H,j,J,g,7,p[8]),J=t(J,B,H,j,v,12,p[9]),j=t(j,J,B,H,b,17,p[10]),H=t(H,j,J,B,S,22,p[11]),B=t(B,H,j,J,w,7,p[12]),J=t(J,B,H,j,C,12,p[13]),j=t(j,J,B,H,_,17,p[14]),H=t(H,j,J,B,A,22,p[15]),B=n(B,H,j,J,d,5,p[16]),J=n(J,B,H,j,x,9,p[17]),j=n(j,J,B,H,S,14,p[18]),H=n(H,j,J,B,u,20,p[19]),B=n(B,H,j,J,l,5,p[20]),J=n(J,B,H,j,b,9,p[21]),j=n(j,J,B,H,A,14,p[22]),H=n(H,j,J,B,m,20,p[23]),B=n(B,H,j,J,v,5,p[24]),J=n(J,B,H,j,_,9,p[25]),j=n(j,J,B,H,y,14,p[26]),H=n(H,j,J,B,g,20,p[27]),B=n(B,H,j,J,C,5,p[28]),J=n(J,B,H,j,h,9,p[29]),j=n(j,J,B,H,q,14,p[30]),H=n(H,j,J,B,w,20,p[31]),B=i(B,H,j,J,l,4,p[32]),J=i(J,B,H,j,g,11,p[33]),j=i(j,J,B,H,S,16,p[34]),H=i(H,j,J,B,_,23,p[35]),B=i(B,H,j,J,d,4,p[36]),J=i(J,B,H,j,m,11,p[37]),j=i(j,J,B,H,q,16,p[38]),H=i(H,j,J,B,b,23,p[39]),B=i(B,H,j,J,C,4,p[40]),J=i(J,B,H,j,u,11,p[41]),j=i(j,J,B,H,y,16,p[42]),H=i(H,j,J,B,x,23,p[43]),B=i(B,H,j,J,v,4,p[44]),J=i(J,B,H,j,w,11,p[45]),j=i(j,J,B,H,A,16,p[46]),H=i(H,j,J,B,h,23,p[47]),B=o(B,H,j,J,u,6,p[48]),J=o(J,B,H,j,q,10,p[49]),j=o(j,J,B,H,_,15,p[50]),H=o(H,j,J,B,l,21,p[51]),B=o(B,H,j,J,w,6,p[52]),J=o(J,B,H,j,y,10,p[53]),j=o(j,J,B,H,b,15,p[54]),H=o(H,j,J,B,d,21,p[55]),B=o(B,H,j,J,g,6,p[56]),J=o(J,B,H,j,A,10,p[57]),j=o(j,J,B,H,x,15,p[58]),H=o(H,j,J,B,C,21,p[59]),B=o(B,H,j,J,m,6,p[60]),J=o(J,B,H,j,S,10,p[61]),j=o(j,J,B,H,h,15,p[62]),H=o(H,j,J,B,v,21,p[63]),a[0]=0|a[0]+B,a[1]=0|a[1]+H,a[2]=0|a[2]+j,a[3]=0|a[3]+J},_doFinalize:function(){var e=this._data,t=e.words,n=8*this._nDataBytes,i=8*e.sigBytes;t[i>>>5]|=128<<24-i%32;var o=r.floor(n/4294967296),s=n;t[(i+64>>>9<<4)+15]=16711935&(o<<8|o>>>24)|4278255360&(o<<24|o>>>8),t[(i+64>>>9<<4)+14]=16711935&(s<<8|s>>>24)|4278255360&(s<<24|s>>>8),e.sigBytes=4*(t.length+1),this._process();for(var c=this._hash,f=c.words,a=0;4>a;a++){var u=f[a];f[a]=16711935&(u<<8|u>>>24)|4278255360&(u<<24|u>>>8)}return c},clone:function(){var e=a.clone.call(this);return e._hash=this._hash.clone(),e}});s.MD5=a._createHelper(d),s.HmacMD5=a._createHmacHelper(d)}(Math),e.MD5});
},{"./core":9}],18:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return e.mode.CFB=function(){function r(e,r,t,i){var o=this._iv;if(o){var n=o.slice(0);this._iv=void 0}else var n=this._prevBlock;i.encryptBlock(n,0);for(var s=0;t>s;s++)e[r+s]^=n[s]}var t=e.lib.BlockCipherMode.extend();return t.Encryptor=t.extend({processBlock:function(e,t){var i=this._cipher,o=i.blockSize;r.call(this,e,t,o,i),this._prevBlock=e.slice(t,t+o)}}),t.Decryptor=t.extend({processBlock:function(e,t){var i=this._cipher,o=i.blockSize,n=e.slice(t,t+o);r.call(this,e,t,o,i),this._prevBlock=n}}),t}(),e.mode.CFB});
},{"./cipher-core":8,"./core":9}],19:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return e.mode.CTRGladman=function(){function r(e){if(255===(255&e>>24)){var r=255&e>>16,t=255&e>>8,i=255&e;255===r?(r=0,255===t?(t=0,255===i?i=0:++i):++t):++r,e=0,e+=r<<16,e+=t<<8,e+=i}else e+=1<<24;return e}function t(e){return 0===(e[0]=r(e[0]))&&(e[1]=r(e[1])),e}var i=e.lib.BlockCipherMode.extend(),n=i.Encryptor=i.extend({processBlock:function(e,r){var i=this._cipher,n=i.blockSize,o=this._iv,c=this._counter;o&&(c=this._counter=o.slice(0),this._iv=void 0),t(c);var s=c.slice(0);i.encryptBlock(s,0);for(var a=0;n>a;a++)e[r+a]^=s[a]}});return i.Decryptor=n,i}(),e.mode.CTRGladman});
},{"./cipher-core":8,"./core":9}],20:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return e.mode.CTR=function(){var r=e.lib.BlockCipherMode.extend(),t=r.Encryptor=r.extend({processBlock:function(e,r){var t=this._cipher,i=t.blockSize,o=this._iv,n=this._counter;o&&(n=this._counter=o.slice(0),this._iv=void 0);var c=n.slice(0);t.encryptBlock(c,0),n[i-1]=0|n[i-1]+1;for(var s=0;i>s;s++)e[r+s]^=c[s]}});return r.Decryptor=t,r}(),e.mode.CTR});
},{"./cipher-core":8,"./core":9}],21:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return e.mode.ECB=function(){var r=e.lib.BlockCipherMode.extend();return r.Encryptor=r.extend({processBlock:function(e,r){this._cipher.encryptBlock(e,r)}}),r.Decryptor=r.extend({processBlock:function(e,r){this._cipher.decryptBlock(e,r)}}),r}(),e.mode.ECB});
},{"./cipher-core":8,"./core":9}],22:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return e.mode.OFB=function(){var r=e.lib.BlockCipherMode.extend(),t=r.Encryptor=r.extend({processBlock:function(e,r){var t=this._cipher,i=t.blockSize,n=this._iv,o=this._keystream;n&&(o=this._keystream=n.slice(0),this._iv=void 0),t.encryptBlock(o,0);for(var c=0;i>c;c++)e[r+c]^=o[c]}});return r.Decryptor=t,r}(),e.mode.OFB});
},{"./cipher-core":8,"./core":9}],23:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return e.pad.AnsiX923={pad:function(e,r){var t=e.sigBytes,i=4*r,n=i-t%i,o=t+n-1;e.clamp(),e.words[o>>>2]|=n<<24-8*(o%4),e.sigBytes+=n},unpad:function(e){var r=255&e.words[e.sigBytes-1>>>2];e.sigBytes-=r}},e.pad.Ansix923});
},{"./cipher-core":8,"./core":9}],24:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return e.pad.Iso10126={pad:function(r,t){var i=4*t,o=i-r.sigBytes%i;r.concat(e.lib.WordArray.random(o-1)).concat(e.lib.WordArray.create([o<<24],1))},unpad:function(e){var r=255&e.words[e.sigBytes-1>>>2];e.sigBytes-=r}},e.pad.Iso10126});
},{"./cipher-core":8,"./core":9}],25:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return e.pad.Iso97971={pad:function(r,t){r.concat(e.lib.WordArray.create([2147483648],1)),e.pad.ZeroPadding.pad(r,t)},unpad:function(r){e.pad.ZeroPadding.unpad(r),r.sigBytes--}},e.pad.Iso97971});
},{"./cipher-core":8,"./core":9}],26:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return e.pad.NoPadding={pad:function(){},unpad:function(){}},e.pad.NoPadding});
},{"./cipher-core":8,"./core":9}],27:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return e.pad.ZeroPadding={pad:function(e,r){var t=4*r;e.clamp(),e.sigBytes+=t-(e.sigBytes%t||t)},unpad:function(e){for(var r=e.words,t=e.sigBytes-1;!(255&r[t>>>2]>>>24-8*(t%4));)t--;e.sigBytes=t+1}},e.pad.ZeroPadding});
},{"./cipher-core":8,"./core":9}],28:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./sha1"),require("./hmac")):"function"==typeof define&&define.amd?define(["./core","./sha1","./hmac"],r):r(e.CryptoJS)})(this,function(e){return function(){var r=e,t=r.lib,n=t.Base,i=t.WordArray,o=r.algo,a=o.SHA1,s=o.HMAC,c=o.PBKDF2=n.extend({cfg:n.extend({keySize:4,hasher:a,iterations:1}),init:function(e){this.cfg=this.cfg.extend(e)},compute:function(e,r){for(var t=this.cfg,n=s.create(t.hasher,e),o=i.create(),a=i.create([1]),c=o.words,f=a.words,u=t.keySize,h=t.iterations;u>c.length;){var d=n.update(r).finalize(a);n.reset();for(var p=d.words,l=p.length,y=d,m=1;h>m;m++){y=n.finalize(y),n.reset();for(var g=y.words,v=0;l>v;v++)p[v]^=g[v]}o.concat(d),f[0]++}return o.sigBytes=4*u,o}});r.PBKDF2=function(e,r,t){return c.create(t).compute(e,r)}}(),e.PBKDF2});
},{"./core":9,"./hmac":14,"./sha1":33}],29:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./enc-base64"),require("./md5"),require("./evpkdf"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./enc-base64","./md5","./evpkdf","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return function(){function r(){for(var e=this._X,r=this._C,t=0;8>t;t++)s[t]=r[t];r[0]=0|r[0]+1295307597+this._b,r[1]=0|r[1]+3545052371+(r[0]>>>0<s[0]>>>0?1:0),r[2]=0|r[2]+886263092+(r[1]>>>0<s[1]>>>0?1:0),r[3]=0|r[3]+1295307597+(r[2]>>>0<s[2]>>>0?1:0),r[4]=0|r[4]+3545052371+(r[3]>>>0<s[3]>>>0?1:0),r[5]=0|r[5]+886263092+(r[4]>>>0<s[4]>>>0?1:0),r[6]=0|r[6]+1295307597+(r[5]>>>0<s[5]>>>0?1:0),r[7]=0|r[7]+3545052371+(r[6]>>>0<s[6]>>>0?1:0),this._b=r[7]>>>0<s[7]>>>0?1:0;for(var t=0;8>t;t++){var i=e[t]+r[t],o=65535&i,n=i>>>16,c=((o*o>>>17)+o*n>>>15)+n*n,f=(0|(4294901760&i)*i)+(0|(65535&i)*i);a[t]=c^f}e[0]=0|a[0]+(a[7]<<16|a[7]>>>16)+(a[6]<<16|a[6]>>>16),e[1]=0|a[1]+(a[0]<<8|a[0]>>>24)+a[7],e[2]=0|a[2]+(a[1]<<16|a[1]>>>16)+(a[0]<<16|a[0]>>>16),e[3]=0|a[3]+(a[2]<<8|a[2]>>>24)+a[1],e[4]=0|a[4]+(a[3]<<16|a[3]>>>16)+(a[2]<<16|a[2]>>>16),e[5]=0|a[5]+(a[4]<<8|a[4]>>>24)+a[3],e[6]=0|a[6]+(a[5]<<16|a[5]>>>16)+(a[4]<<16|a[4]>>>16),e[7]=0|a[7]+(a[6]<<8|a[6]>>>24)+a[5]}var t=e,i=t.lib,o=i.StreamCipher,n=t.algo,c=[],s=[],a=[],f=n.RabbitLegacy=o.extend({_doReset:function(){var e=this._key.words,t=this.cfg.iv,i=this._X=[e[0],e[3]<<16|e[2]>>>16,e[1],e[0]<<16|e[3]>>>16,e[2],e[1]<<16|e[0]>>>16,e[3],e[2]<<16|e[1]>>>16],o=this._C=[e[2]<<16|e[2]>>>16,4294901760&e[0]|65535&e[1],e[3]<<16|e[3]>>>16,4294901760&e[1]|65535&e[2],e[0]<<16|e[0]>>>16,4294901760&e[2]|65535&e[3],e[1]<<16|e[1]>>>16,4294901760&e[3]|65535&e[0]];this._b=0;for(var n=0;4>n;n++)r.call(this);for(var n=0;8>n;n++)o[n]^=i[7&n+4];if(t){var c=t.words,s=c[0],a=c[1],f=16711935&(s<<8|s>>>24)|4278255360&(s<<24|s>>>8),u=16711935&(a<<8|a>>>24)|4278255360&(a<<24|a>>>8),h=f>>>16|4294901760&u,d=u<<16|65535&f;o[0]^=f,o[1]^=h,o[2]^=u,o[3]^=d,o[4]^=f,o[5]^=h,o[6]^=u,o[7]^=d;for(var n=0;4>n;n++)r.call(this)}},_doProcessBlock:function(e,t){var i=this._X;r.call(this),c[0]=i[0]^i[5]>>>16^i[3]<<16,c[1]=i[2]^i[7]>>>16^i[5]<<16,c[2]=i[4]^i[1]>>>16^i[7]<<16,c[3]=i[6]^i[3]>>>16^i[1]<<16;for(var o=0;4>o;o++)c[o]=16711935&(c[o]<<8|c[o]>>>24)|4278255360&(c[o]<<24|c[o]>>>8),e[t+o]^=c[o]},blockSize:4,ivSize:2});t.RabbitLegacy=o._createHelper(f)}(),e.RabbitLegacy});
},{"./cipher-core":8,"./core":9,"./enc-base64":10,"./evpkdf":12,"./md5":17}],30:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./enc-base64"),require("./md5"),require("./evpkdf"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./enc-base64","./md5","./evpkdf","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return function(){function r(){for(var e=this._X,r=this._C,t=0;8>t;t++)s[t]=r[t];r[0]=0|r[0]+1295307597+this._b,r[1]=0|r[1]+3545052371+(r[0]>>>0<s[0]>>>0?1:0),r[2]=0|r[2]+886263092+(r[1]>>>0<s[1]>>>0?1:0),r[3]=0|r[3]+1295307597+(r[2]>>>0<s[2]>>>0?1:0),r[4]=0|r[4]+3545052371+(r[3]>>>0<s[3]>>>0?1:0),r[5]=0|r[5]+886263092+(r[4]>>>0<s[4]>>>0?1:0),r[6]=0|r[6]+1295307597+(r[5]>>>0<s[5]>>>0?1:0),r[7]=0|r[7]+3545052371+(r[6]>>>0<s[6]>>>0?1:0),this._b=r[7]>>>0<s[7]>>>0?1:0;for(var t=0;8>t;t++){var i=e[t]+r[t],o=65535&i,n=i>>>16,c=((o*o>>>17)+o*n>>>15)+n*n,f=(0|(4294901760&i)*i)+(0|(65535&i)*i);a[t]=c^f}e[0]=0|a[0]+(a[7]<<16|a[7]>>>16)+(a[6]<<16|a[6]>>>16),e[1]=0|a[1]+(a[0]<<8|a[0]>>>24)+a[7],e[2]=0|a[2]+(a[1]<<16|a[1]>>>16)+(a[0]<<16|a[0]>>>16),e[3]=0|a[3]+(a[2]<<8|a[2]>>>24)+a[1],e[4]=0|a[4]+(a[3]<<16|a[3]>>>16)+(a[2]<<16|a[2]>>>16),e[5]=0|a[5]+(a[4]<<8|a[4]>>>24)+a[3],e[6]=0|a[6]+(a[5]<<16|a[5]>>>16)+(a[4]<<16|a[4]>>>16),e[7]=0|a[7]+(a[6]<<8|a[6]>>>24)+a[5]}var t=e,i=t.lib,o=i.StreamCipher,n=t.algo,c=[],s=[],a=[],f=n.Rabbit=o.extend({_doReset:function(){for(var e=this._key.words,t=this.cfg.iv,i=0;4>i;i++)e[i]=16711935&(e[i]<<8|e[i]>>>24)|4278255360&(e[i]<<24|e[i]>>>8);var o=this._X=[e[0],e[3]<<16|e[2]>>>16,e[1],e[0]<<16|e[3]>>>16,e[2],e[1]<<16|e[0]>>>16,e[3],e[2]<<16|e[1]>>>16],n=this._C=[e[2]<<16|e[2]>>>16,4294901760&e[0]|65535&e[1],e[3]<<16|e[3]>>>16,4294901760&e[1]|65535&e[2],e[0]<<16|e[0]>>>16,4294901760&e[2]|65535&e[3],e[1]<<16|e[1]>>>16,4294901760&e[3]|65535&e[0]];this._b=0;for(var i=0;4>i;i++)r.call(this);for(var i=0;8>i;i++)n[i]^=o[7&i+4];if(t){var c=t.words,s=c[0],a=c[1],f=16711935&(s<<8|s>>>24)|4278255360&(s<<24|s>>>8),u=16711935&(a<<8|a>>>24)|4278255360&(a<<24|a>>>8),h=f>>>16|4294901760&u,d=u<<16|65535&f;n[0]^=f,n[1]^=h,n[2]^=u,n[3]^=d,n[4]^=f,n[5]^=h,n[6]^=u,n[7]^=d;for(var i=0;4>i;i++)r.call(this)}},_doProcessBlock:function(e,t){var i=this._X;r.call(this),c[0]=i[0]^i[5]>>>16^i[3]<<16,c[1]=i[2]^i[7]>>>16^i[5]<<16,c[2]=i[4]^i[1]>>>16^i[7]<<16,c[3]=i[6]^i[3]>>>16^i[1]<<16;for(var o=0;4>o;o++)c[o]=16711935&(c[o]<<8|c[o]>>>24)|4278255360&(c[o]<<24|c[o]>>>8),e[t+o]^=c[o]},blockSize:4,ivSize:2});t.Rabbit=o._createHelper(f)}(),e.Rabbit});
},{"./cipher-core":8,"./core":9,"./enc-base64":10,"./evpkdf":12,"./md5":17}],31:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./enc-base64"),require("./md5"),require("./evpkdf"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./enc-base64","./md5","./evpkdf","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return function(){function r(){for(var e=this._S,r=this._i,t=this._j,i=0,o=0;4>o;o++){r=(r+1)%256,t=(t+e[r])%256;var n=e[r];e[r]=e[t],e[t]=n,i|=e[(e[r]+e[t])%256]<<24-8*o}return this._i=r,this._j=t,i}var t=e,i=t.lib,o=i.StreamCipher,n=t.algo,c=n.RC4=o.extend({_doReset:function(){for(var e=this._key,r=e.words,t=e.sigBytes,i=this._S=[],o=0;256>o;o++)i[o]=o;for(var o=0,n=0;256>o;o++){var c=o%t,s=255&r[c>>>2]>>>24-8*(c%4);n=(n+i[o]+s)%256;var a=i[o];i[o]=i[n],i[n]=a}this._i=this._j=0},_doProcessBlock:function(e,t){e[t]^=r.call(this)},keySize:8,ivSize:0});t.RC4=o._createHelper(c);var s=n.RC4Drop=c.extend({cfg:c.cfg.extend({drop:192}),_doReset:function(){c._doReset.call(this);for(var e=this.cfg.drop;e>0;e--)r.call(this)}});t.RC4Drop=o._createHelper(s)}(),e.RC4});
},{"./cipher-core":8,"./core":9,"./enc-base64":10,"./evpkdf":12,"./md5":17}],32:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core")):"function"==typeof define&&define.amd?define(["./core"],r):r(e.CryptoJS)})(this,function(e){return function(){function r(e,r,t){return e^r^t}function t(e,r,t){return e&r|~e&t}function n(e,r,t){return(e|~r)^t}function i(e,r,t){return e&t|r&~t}function o(e,r,t){return e^(r|~t)}function s(e,r){return e<<r|e>>>32-r}var a=e,c=a.lib,f=c.WordArray,u=c.Hasher,h=a.algo,d=f.create([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,7,4,13,1,10,6,15,3,12,0,9,5,2,14,11,8,3,10,14,4,9,15,8,1,2,7,0,6,13,11,5,12,1,9,11,10,0,8,12,4,13,3,7,15,14,5,6,2,4,0,5,9,7,12,2,10,14,1,3,8,11,6,15,13]),p=f.create([5,14,7,0,9,2,11,4,13,6,15,8,1,10,3,12,6,11,3,7,0,13,5,10,14,15,8,12,4,9,1,2,15,5,1,3,7,14,6,9,11,8,12,2,10,0,4,13,8,6,4,1,3,11,15,0,5,12,2,13,9,7,10,14,12,15,10,4,1,5,8,7,6,2,13,14,0,3,9,11]),l=f.create([11,14,15,12,5,8,7,9,11,13,14,15,6,7,9,8,7,6,8,13,11,9,7,15,7,12,15,9,11,7,13,12,11,13,6,7,14,9,13,15,14,8,13,6,5,12,7,5,11,12,14,15,14,15,9,8,9,14,5,6,8,6,5,12,9,15,5,11,6,8,13,12,5,12,13,14,11,8,5,6]),y=f.create([8,9,9,11,13,15,15,5,7,7,8,11,14,14,12,6,9,13,15,7,12,8,9,11,7,7,12,7,6,15,13,11,9,7,15,11,8,6,6,14,12,13,5,14,13,13,7,5,15,5,8,11,14,14,6,14,6,9,12,9,12,5,15,8,8,5,12,9,12,5,14,6,8,13,6,5,15,13,11,11]),m=f.create([0,1518500249,1859775393,2400959708,2840853838]),x=f.create([1352829926,1548603684,1836072691,2053994217,0]),g=h.RIPEMD160=u.extend({_doReset:function(){this._hash=f.create([1732584193,4023233417,2562383102,271733878,3285377520])},_doProcessBlock:function(e,a){for(var c=0;16>c;c++){var f=a+c,u=e[f];e[f]=16711935&(u<<8|u>>>24)|4278255360&(u<<24|u>>>8)}var h,g,v,_,w,q,H,S,b,A,B=this._hash.words,C=m.words,j=x.words,J=d.words,z=p.words,M=l.words,W=y.words;q=h=B[0],H=g=B[1],S=v=B[2],b=_=B[3],A=w=B[4];for(var D,c=0;80>c;c+=1)D=0|h+e[a+J[c]],D+=16>c?r(g,v,_)+C[0]:32>c?t(g,v,_)+C[1]:48>c?n(g,v,_)+C[2]:64>c?i(g,v,_)+C[3]:o(g,v,_)+C[4],D=0|D,D=s(D,M[c]),D=0|D+w,h=w,w=_,_=s(v,10),v=g,g=D,D=0|q+e[a+z[c]],D+=16>c?o(H,S,b)+j[0]:32>c?i(H,S,b)+j[1]:48>c?n(H,S,b)+j[2]:64>c?t(H,S,b)+j[3]:r(H,S,b)+j[4],D=0|D,D=s(D,W[c]),D=0|D+A,q=A,A=b,b=s(S,10),S=H,H=D;D=0|B[1]+v+b,B[1]=0|B[2]+_+A,B[2]=0|B[3]+w+q,B[3]=0|B[4]+h+H,B[4]=0|B[0]+g+S,B[0]=D},_doFinalize:function(){var e=this._data,r=e.words,t=8*this._nDataBytes,n=8*e.sigBytes;r[n>>>5]|=128<<24-n%32,r[(n+64>>>9<<4)+14]=16711935&(t<<8|t>>>24)|4278255360&(t<<24|t>>>8),e.sigBytes=4*(r.length+1),this._process();for(var i=this._hash,o=i.words,s=0;5>s;s++){var a=o[s];o[s]=16711935&(a<<8|a>>>24)|4278255360&(a<<24|a>>>8)}return i},clone:function(){var e=u.clone.call(this);return e._hash=this._hash.clone(),e}});a.RIPEMD160=u._createHelper(g),a.HmacRIPEMD160=u._createHmacHelper(g)}(Math),e.RIPEMD160});
},{"./core":9}],33:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core")):"function"==typeof define&&define.amd?define(["./core"],r):r(e.CryptoJS)})(this,function(e){return function(){var r=e,t=r.lib,n=t.WordArray,i=t.Hasher,o=r.algo,s=[],c=o.SHA1=i.extend({_doReset:function(){this._hash=new n.init([1732584193,4023233417,2562383102,271733878,3285377520])},_doProcessBlock:function(e,r){for(var t=this._hash.words,n=t[0],i=t[1],o=t[2],c=t[3],a=t[4],f=0;80>f;f++){if(16>f)s[f]=0|e[r+f];else{var u=s[f-3]^s[f-8]^s[f-14]^s[f-16];s[f]=u<<1|u>>>31}var d=(n<<5|n>>>27)+a+s[f];d+=20>f?(i&o|~i&c)+1518500249:40>f?(i^o^c)+1859775393:60>f?(i&o|i&c|o&c)-1894007588:(i^o^c)-899497514,a=c,c=o,o=i<<30|i>>>2,i=n,n=d}t[0]=0|t[0]+n,t[1]=0|t[1]+i,t[2]=0|t[2]+o,t[3]=0|t[3]+c,t[4]=0|t[4]+a},_doFinalize:function(){var e=this._data,r=e.words,t=8*this._nDataBytes,n=8*e.sigBytes;return r[n>>>5]|=128<<24-n%32,r[(n+64>>>9<<4)+14]=Math.floor(t/4294967296),r[(n+64>>>9<<4)+15]=t,e.sigBytes=4*r.length,this._process(),this._hash},clone:function(){var e=i.clone.call(this);return e._hash=this._hash.clone(),e}});r.SHA1=i._createHelper(c),r.HmacSHA1=i._createHmacHelper(c)}(),e.SHA1});
},{"./core":9}],34:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./sha256")):"function"==typeof define&&define.amd?define(["./core","./sha256"],r):r(e.CryptoJS)})(this,function(e){return function(){var r=e,t=r.lib,n=t.WordArray,i=r.algo,o=i.SHA256,s=i.SHA224=o.extend({_doReset:function(){this._hash=new n.init([3238371032,914150663,812702999,4144912697,4290775857,1750603025,1694076839,3204075428])},_doFinalize:function(){var e=o._doFinalize.call(this);return e.sigBytes-=4,e}});r.SHA224=o._createHelper(s),r.HmacSHA224=o._createHmacHelper(s)}(),e.SHA224});
},{"./core":9,"./sha256":35}],35:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core")):"function"==typeof define&&define.amd?define(["./core"],r):r(e.CryptoJS)})(this,function(e){return function(r){var t=e,n=t.lib,i=n.WordArray,o=n.Hasher,s=t.algo,c=[],a=[];(function(){function e(e){for(var t=r.sqrt(e),n=2;t>=n;n++)if(!(e%n))return!1;return!0}function t(e){return 0|4294967296*(e-(0|e))}for(var n=2,i=0;64>i;)e(n)&&(8>i&&(c[i]=t(r.pow(n,.5))),a[i]=t(r.pow(n,1/3)),i++),n++})();var f=[],u=s.SHA256=o.extend({_doReset:function(){this._hash=new i.init(c.slice(0))},_doProcessBlock:function(e,r){for(var t=this._hash.words,n=t[0],i=t[1],o=t[2],s=t[3],c=t[4],u=t[5],d=t[6],p=t[7],h=0;64>h;h++){if(16>h)f[h]=0|e[r+h];else{var y=f[h-15],l=(y<<25|y>>>7)^(y<<14|y>>>18)^y>>>3,m=f[h-2],x=(m<<15|m>>>17)^(m<<13|m>>>19)^m>>>10;f[h]=l+f[h-7]+x+f[h-16]}var v=c&u^~c&d,q=n&i^n&o^i&o,g=(n<<30|n>>>2)^(n<<19|n>>>13)^(n<<10|n>>>22),_=(c<<26|c>>>6)^(c<<21|c>>>11)^(c<<7|c>>>25),b=p+_+v+a[h]+f[h],S=g+q;p=d,d=u,u=c,c=0|s+b,s=o,o=i,i=n,n=0|b+S}t[0]=0|t[0]+n,t[1]=0|t[1]+i,t[2]=0|t[2]+o,t[3]=0|t[3]+s,t[4]=0|t[4]+c,t[5]=0|t[5]+u,t[6]=0|t[6]+d,t[7]=0|t[7]+p},_doFinalize:function(){var e=this._data,t=e.words,n=8*this._nDataBytes,i=8*e.sigBytes;return t[i>>>5]|=128<<24-i%32,t[(i+64>>>9<<4)+14]=r.floor(n/4294967296),t[(i+64>>>9<<4)+15]=n,e.sigBytes=4*t.length,this._process(),this._hash},clone:function(){var e=o.clone.call(this);return e._hash=this._hash.clone(),e}});t.SHA256=o._createHelper(u),t.HmacSHA256=o._createHmacHelper(u)}(Math),e.SHA256});
},{"./core":9}],36:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./x64-core")):"function"==typeof define&&define.amd?define(["./core","./x64-core"],r):r(e.CryptoJS)})(this,function(e){return function(r){var t=e,n=t.lib,i=n.WordArray,o=n.Hasher,a=t.x64,s=a.Word,c=t.algo,f=[],u=[],h=[];(function(){for(var e=1,r=0,t=0;24>t;t++){f[e+5*r]=(t+1)*(t+2)/2%64;var n=r%5,i=(2*e+3*r)%5;e=n,r=i}for(var e=0;5>e;e++)for(var r=0;5>r;r++)u[e+5*r]=r+5*((2*e+3*r)%5);for(var o=1,a=0;24>a;a++){for(var c=0,d=0,p=0;7>p;p++){if(1&o){var l=(1<<p)-1;32>l?d^=1<<l:c^=1<<l-32}128&o?o=113^o<<1:o<<=1}h[a]=s.create(c,d)}})();var d=[];(function(){for(var e=0;25>e;e++)d[e]=s.create()})();var p=c.SHA3=o.extend({cfg:o.cfg.extend({outputLength:512}),_doReset:function(){for(var e=this._state=[],r=0;25>r;r++)e[r]=new s.init;this.blockSize=(1600-2*this.cfg.outputLength)/32},_doProcessBlock:function(e,r){for(var t=this._state,n=this.blockSize/2,i=0;n>i;i++){var o=e[r+2*i],a=e[r+2*i+1];o=16711935&(o<<8|o>>>24)|4278255360&(o<<24|o>>>8),a=16711935&(a<<8|a>>>24)|4278255360&(a<<24|a>>>8);var s=t[i];s.high^=a,s.low^=o}for(var c=0;24>c;c++){for(var p=0;5>p;p++){for(var l=0,y=0,m=0;5>m;m++){var s=t[p+5*m];l^=s.high,y^=s.low}var v=d[p];v.high=l,v.low=y}for(var p=0;5>p;p++)for(var g=d[(p+4)%5],x=d[(p+1)%5],w=x.high,_=x.low,l=g.high^(w<<1|_>>>31),y=g.low^(_<<1|w>>>31),m=0;5>m;m++){var s=t[p+5*m];s.high^=l,s.low^=y}for(var q=1;25>q;q++){var s=t[q],H=s.high,S=s.low,b=f[q];if(32>b)var l=H<<b|S>>>32-b,y=S<<b|H>>>32-b;else var l=S<<b-32|H>>>64-b,y=H<<b-32|S>>>64-b;var A=d[u[q]];A.high=l,A.low=y}var B=d[0],C=t[0];B.high=C.high,B.low=C.low;for(var p=0;5>p;p++)for(var m=0;5>m;m++){var q=p+5*m,s=t[q],j=d[q],z=d[(p+1)%5+5*m],J=d[(p+2)%5+5*m];s.high=j.high^~z.high&J.high,s.low=j.low^~z.low&J.low}var s=t[0],M=h[c];s.high^=M.high,s.low^=M.low}},_doFinalize:function(){var e=this._data,t=e.words;8*this._nDataBytes;var n=8*e.sigBytes,o=32*this.blockSize;t[n>>>5]|=1<<24-n%32,t[(r.ceil((n+1)/o)*o>>>5)-1]|=128,e.sigBytes=4*t.length,this._process();for(var a=this._state,s=this.cfg.outputLength/8,c=s/8,f=[],u=0;c>u;u++){var h=a[u],d=h.high,p=h.low;d=16711935&(d<<8|d>>>24)|4278255360&(d<<24|d>>>8),p=16711935&(p<<8|p>>>24)|4278255360&(p<<24|p>>>8),f.push(p),f.push(d)}return new i.init(f,s)},clone:function(){for(var e=o.clone.call(this),r=e._state=this._state.slice(0),t=0;25>t;t++)r[t]=r[t].clone();return e}});t.SHA3=o._createHelper(p),t.HmacSHA3=o._createHmacHelper(p)}(Math),e.SHA3});
},{"./core":9,"./x64-core":40}],37:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./x64-core"),require("./sha512")):"function"==typeof define&&define.amd?define(["./core","./x64-core","./sha512"],r):r(e.CryptoJS)})(this,function(e){return function(){var r=e,t=r.x64,n=t.Word,i=t.WordArray,o=r.algo,s=o.SHA512,c=o.SHA384=s.extend({_doReset:function(){this._hash=new i.init([new n.init(3418070365,3238371032),new n.init(1654270250,914150663),new n.init(2438529370,812702999),new n.init(355462360,4144912697),new n.init(1731405415,4290775857),new n.init(2394180231,1750603025),new n.init(3675008525,1694076839),new n.init(1203062813,3204075428)])},_doFinalize:function(){var e=s._doFinalize.call(this);return e.sigBytes-=16,e}});r.SHA384=s._createHelper(c),r.HmacSHA384=s._createHmacHelper(c)}(),e.SHA384});
},{"./core":9,"./sha512":38,"./x64-core":40}],38:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./x64-core")):"function"==typeof define&&define.amd?define(["./core","./x64-core"],r):r(e.CryptoJS)})(this,function(e){return function(){function r(){return s.create.apply(s,arguments)}var t=e,n=t.lib,i=n.Hasher,o=t.x64,s=o.Word,a=o.WordArray,c=t.algo,f=[r(1116352408,3609767458),r(1899447441,602891725),r(3049323471,3964484399),r(3921009573,2173295548),r(961987163,4081628472),r(1508970993,3053834265),r(2453635748,2937671579),r(2870763221,3664609560),r(3624381080,2734883394),r(310598401,1164996542),r(607225278,1323610764),r(1426881987,3590304994),r(1925078388,4068182383),r(2162078206,991336113),r(2614888103,633803317),r(3248222580,3479774868),r(3835390401,2666613458),r(4022224774,944711139),r(264347078,2341262773),r(604807628,2007800933),r(770255983,1495990901),r(1249150122,1856431235),r(1555081692,3175218132),r(1996064986,2198950837),r(2554220882,3999719339),r(2821834349,766784016),r(2952996808,2566594879),r(3210313671,3203337956),r(3336571891,1034457026),r(3584528711,2466948901),r(113926993,3758326383),r(338241895,168717936),r(666307205,1188179964),r(773529912,1546045734),r(1294757372,1522805485),r(1396182291,2643833823),r(1695183700,2343527390),r(1986661051,1014477480),r(2177026350,1206759142),r(2456956037,344077627),r(2730485921,1290863460),r(2820302411,3158454273),r(3259730800,3505952657),r(3345764771,106217008),r(3516065817,3606008344),r(3600352804,1432725776),r(4094571909,1467031594),r(275423344,851169720),r(430227734,3100823752),r(506948616,1363258195),r(659060556,3750685593),r(883997877,3785050280),r(958139571,3318307427),r(1322822218,3812723403),r(1537002063,2003034995),r(1747873779,3602036899),r(1955562222,1575990012),r(2024104815,1125592928),r(2227730452,2716904306),r(2361852424,442776044),r(2428436474,593698344),r(2756734187,3733110249),r(3204031479,2999351573),r(3329325298,3815920427),r(3391569614,3928383900),r(3515267271,566280711),r(3940187606,3454069534),r(4118630271,4000239992),r(116418474,1914138554),r(174292421,2731055270),r(289380356,3203993006),r(460393269,320620315),r(685471733,587496836),r(852142971,1086792851),r(1017036298,365543100),r(1126000580,2618297676),r(1288033470,3409855158),r(1501505948,4234509866),r(1607167915,987167468),r(1816402316,1246189591)],u=[];(function(){for(var e=0;80>e;e++)u[e]=r()})();var h=c.SHA512=i.extend({_doReset:function(){this._hash=new a.init([new s.init(1779033703,4089235720),new s.init(3144134277,2227873595),new s.init(1013904242,4271175723),new s.init(2773480762,1595750129),new s.init(1359893119,2917565137),new s.init(2600822924,725511199),new s.init(528734635,4215389547),new s.init(1541459225,327033209)])},_doProcessBlock:function(e,r){for(var t=this._hash.words,n=t[0],i=t[1],o=t[2],s=t[3],a=t[4],c=t[5],h=t[6],d=t[7],p=n.high,l=n.low,y=i.high,m=i.low,x=o.high,g=o.low,v=s.high,w=s.low,_=a.high,q=a.low,H=c.high,S=c.low,b=h.high,A=h.low,B=d.high,C=d.low,j=p,J=l,z=y,W=m,U=x,k=g,M=v,D=w,F=_,P=q,R=H,I=S,O=b,L=A,E=B,X=C,$=0;80>$;$++){var T=u[$];if(16>$)var G=T.high=0|e[r+2*$],K=T.low=0|e[r+2*$+1];else{var N=u[$-15],Q=N.high,V=N.low,Y=(Q>>>1|V<<31)^(Q>>>8|V<<24)^Q>>>7,Z=(V>>>1|Q<<31)^(V>>>8|Q<<24)^(V>>>7|Q<<25),er=u[$-2],rr=er.high,tr=er.low,nr=(rr>>>19|tr<<13)^(rr<<3|tr>>>29)^rr>>>6,ir=(tr>>>19|rr<<13)^(tr<<3|rr>>>29)^(tr>>>6|rr<<26),or=u[$-7],sr=or.high,ar=or.low,cr=u[$-16],fr=cr.high,ur=cr.low,K=Z+ar,G=Y+sr+(Z>>>0>K>>>0?1:0),K=K+ir,G=G+nr+(ir>>>0>K>>>0?1:0),K=K+ur,G=G+fr+(ur>>>0>K>>>0?1:0);T.high=G,T.low=K}var hr=F&R^~F&O,dr=P&I^~P&L,pr=j&z^j&U^z&U,lr=J&W^J&k^W&k,yr=(j>>>28|J<<4)^(j<<30|J>>>2)^(j<<25|J>>>7),mr=(J>>>28|j<<4)^(J<<30|j>>>2)^(J<<25|j>>>7),xr=(F>>>14|P<<18)^(F>>>18|P<<14)^(F<<23|P>>>9),gr=(P>>>14|F<<18)^(P>>>18|F<<14)^(P<<23|F>>>9),vr=f[$],wr=vr.high,_r=vr.low,qr=X+gr,Hr=E+xr+(X>>>0>qr>>>0?1:0),qr=qr+dr,Hr=Hr+hr+(dr>>>0>qr>>>0?1:0),qr=qr+_r,Hr=Hr+wr+(_r>>>0>qr>>>0?1:0),qr=qr+K,Hr=Hr+G+(K>>>0>qr>>>0?1:0),Sr=mr+lr,br=yr+pr+(mr>>>0>Sr>>>0?1:0);E=O,X=L,O=R,L=I,R=F,I=P,P=0|D+qr,F=0|M+Hr+(D>>>0>P>>>0?1:0),M=U,D=k,U=z,k=W,z=j,W=J,J=0|qr+Sr,j=0|Hr+br+(qr>>>0>J>>>0?1:0)}l=n.low=l+J,n.high=p+j+(J>>>0>l>>>0?1:0),m=i.low=m+W,i.high=y+z+(W>>>0>m>>>0?1:0),g=o.low=g+k,o.high=x+U+(k>>>0>g>>>0?1:0),w=s.low=w+D,s.high=v+M+(D>>>0>w>>>0?1:0),q=a.low=q+P,a.high=_+F+(P>>>0>q>>>0?1:0),S=c.low=S+I,c.high=H+R+(I>>>0>S>>>0?1:0),A=h.low=A+L,h.high=b+O+(L>>>0>A>>>0?1:0),C=d.low=C+X,d.high=B+E+(X>>>0>C>>>0?1:0)},_doFinalize:function(){var e=this._data,r=e.words,t=8*this._nDataBytes,n=8*e.sigBytes;r[n>>>5]|=128<<24-n%32,r[(n+128>>>10<<5)+30]=Math.floor(t/4294967296),r[(n+128>>>10<<5)+31]=t,e.sigBytes=4*r.length,this._process();var i=this._hash.toX32();return i},clone:function(){var e=i.clone.call(this);return e._hash=this._hash.clone(),e},blockSize:32});t.SHA512=i._createHelper(h),t.HmacSHA512=i._createHmacHelper(h)}(),e.SHA512});
},{"./core":9,"./x64-core":40}],39:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core"),require("./enc-base64"),require("./md5"),require("./evpkdf"),require("./cipher-core")):"function"==typeof define&&define.amd?define(["./core","./enc-base64","./md5","./evpkdf","./cipher-core"],r):r(e.CryptoJS)})(this,function(e){return function(){function r(e,r){var t=(this._lBlock>>>e^this._rBlock)&r;this._rBlock^=t,this._lBlock^=t<<e}function t(e,r){var t=(this._rBlock>>>e^this._lBlock)&r;this._lBlock^=t,this._rBlock^=t<<e}var i=e,o=i.lib,n=o.WordArray,c=o.BlockCipher,s=i.algo,a=[57,49,41,33,25,17,9,1,58,50,42,34,26,18,10,2,59,51,43,35,27,19,11,3,60,52,44,36,63,55,47,39,31,23,15,7,62,54,46,38,30,22,14,6,61,53,45,37,29,21,13,5,28,20,12,4],f=[14,17,11,24,1,5,3,28,15,6,21,10,23,19,12,4,26,8,16,7,27,20,13,2,41,52,31,37,47,55,30,40,51,45,33,48,44,49,39,56,34,53,46,42,50,36,29,32],u=[1,2,4,6,8,10,12,14,15,17,19,21,23,25,27,28],h=[{0:8421888,268435456:32768,536870912:8421378,805306368:2,1073741824:512,1342177280:8421890,1610612736:8389122,1879048192:8388608,2147483648:514,2415919104:8389120,2684354560:33280,2952790016:8421376,3221225472:32770,3489660928:8388610,3758096384:0,4026531840:33282,134217728:0,402653184:8421890,671088640:33282,939524096:32768,1207959552:8421888,1476395008:512,1744830464:8421378,2013265920:2,2281701376:8389120,2550136832:33280,2818572288:8421376,3087007744:8389122,3355443200:8388610,3623878656:32770,3892314112:514,4160749568:8388608,1:32768,268435457:2,536870913:8421888,805306369:8388608,1073741825:8421378,1342177281:33280,1610612737:512,1879048193:8389122,2147483649:8421890,2415919105:8421376,2684354561:8388610,2952790017:33282,3221225473:514,3489660929:8389120,3758096385:32770,4026531841:0,134217729:8421890,402653185:8421376,671088641:8388608,939524097:512,1207959553:32768,1476395009:8388610,1744830465:2,2013265921:33282,2281701377:32770,2550136833:8389122,2818572289:514,3087007745:8421888,3355443201:8389120,3623878657:0,3892314113:33280,4160749569:8421378},{0:1074282512,16777216:16384,33554432:524288,50331648:1074266128,67108864:1073741840,83886080:1074282496,100663296:1073758208,117440512:16,134217728:540672,150994944:1073758224,167772160:1073741824,184549376:540688,201326592:524304,218103808:0,234881024:16400,251658240:1074266112,8388608:1073758208,25165824:540688,41943040:16,58720256:1073758224,75497472:1074282512,92274688:1073741824,109051904:524288,125829120:1074266128,142606336:524304,159383552:0,176160768:16384,192937984:1074266112,209715200:1073741840,226492416:540672,243269632:1074282496,260046848:16400,268435456:0,285212672:1074266128,301989888:1073758224,318767104:1074282496,335544320:1074266112,352321536:16,369098752:540688,385875968:16384,402653184:16400,419430400:524288,436207616:524304,452984832:1073741840,469762048:540672,486539264:1073758208,503316480:1073741824,520093696:1074282512,276824064:540688,293601280:524288,310378496:1074266112,327155712:16384,343932928:1073758208,360710144:1074282512,377487360:16,394264576:1073741824,411041792:1074282496,427819008:1073741840,444596224:1073758224,461373440:524304,478150656:0,494927872:16400,511705088:1074266128,528482304:540672},{0:260,1048576:0,2097152:67109120,3145728:65796,4194304:65540,5242880:67108868,6291456:67174660,7340032:67174400,8388608:67108864,9437184:67174656,10485760:65792,11534336:67174404,12582912:67109124,13631488:65536,14680064:4,15728640:256,524288:67174656,1572864:67174404,2621440:0,3670016:67109120,4718592:67108868,5767168:65536,6815744:65540,7864320:260,8912896:4,9961472:256,11010048:67174400,12058624:65796,13107200:65792,14155776:67109124,15204352:67174660,16252928:67108864,16777216:67174656,17825792:65540,18874368:65536,19922944:67109120,20971520:256,22020096:67174660,23068672:67108868,24117248:0,25165824:67109124,26214400:67108864,27262976:4,28311552:65792,29360128:67174400,30408704:260,31457280:65796,32505856:67174404,17301504:67108864,18350080:260,19398656:67174656,20447232:0,21495808:65540,22544384:67109120,23592960:256,24641536:67174404,25690112:65536,26738688:67174660,27787264:65796,28835840:67108868,29884416:67109124,30932992:67174400,31981568:4,33030144:65792},{0:2151682048,65536:2147487808,131072:4198464,196608:2151677952,262144:0,327680:4198400,393216:2147483712,458752:4194368,524288:2147483648,589824:4194304,655360:64,720896:2147487744,786432:2151678016,851968:4160,917504:4096,983040:2151682112,32768:2147487808,98304:64,163840:2151678016,229376:2147487744,294912:4198400,360448:2151682112,425984:0,491520:2151677952,557056:4096,622592:2151682048,688128:4194304,753664:4160,819200:2147483648,884736:4194368,950272:4198464,1015808:2147483712,1048576:4194368,1114112:4198400,1179648:2147483712,1245184:0,1310720:4160,1376256:2151678016,1441792:2151682048,1507328:2147487808,1572864:2151682112,1638400:2147483648,1703936:2151677952,1769472:4198464,1835008:2147487744,1900544:4194304,1966080:64,2031616:4096,1081344:2151677952,1146880:2151682112,1212416:0,1277952:4198400,1343488:4194368,1409024:2147483648,1474560:2147487808,1540096:64,1605632:2147483712,1671168:4096,1736704:2147487744,1802240:2151678016,1867776:4160,1933312:2151682048,1998848:4194304,2064384:4198464},{0:128,4096:17039360,8192:262144,12288:536870912,16384:537133184,20480:16777344,24576:553648256,28672:262272,32768:16777216,36864:537133056,40960:536871040,45056:553910400,49152:553910272,53248:0,57344:17039488,61440:553648128,2048:17039488,6144:553648256,10240:128,14336:17039360,18432:262144,22528:537133184,26624:553910272,30720:536870912,34816:537133056,38912:0,43008:553910400,47104:16777344,51200:536871040,55296:553648128,59392:16777216,63488:262272,65536:262144,69632:128,73728:536870912,77824:553648256,81920:16777344,86016:553910272,90112:537133184,94208:16777216,98304:553910400,102400:553648128,106496:17039360,110592:537133056,114688:262272,118784:536871040,122880:0,126976:17039488,67584:553648256,71680:16777216,75776:17039360,79872:537133184,83968:536870912,88064:17039488,92160:128,96256:553910272,100352:262272,104448:553910400,108544:0,112640:553648128,116736:16777344,120832:262144,124928:537133056,129024:536871040},{0:268435464,256:8192,512:270532608,768:270540808,1024:268443648,1280:2097152,1536:2097160,1792:268435456,2048:0,2304:268443656,2560:2105344,2816:8,3072:270532616,3328:2105352,3584:8200,3840:270540800,128:270532608,384:270540808,640:8,896:2097152,1152:2105352,1408:268435464,1664:268443648,1920:8200,2176:2097160,2432:8192,2688:268443656,2944:270532616,3200:0,3456:270540800,3712:2105344,3968:268435456,4096:268443648,4352:270532616,4608:270540808,4864:8200,5120:2097152,5376:268435456,5632:268435464,5888:2105344,6144:2105352,6400:0,6656:8,6912:270532608,7168:8192,7424:268443656,7680:270540800,7936:2097160,4224:8,4480:2105344,4736:2097152,4992:268435464,5248:268443648,5504:8200,5760:270540808,6016:270532608,6272:270540800,6528:270532616,6784:8192,7040:2105352,7296:2097160,7552:0,7808:268435456,8064:268443656},{0:1048576,16:33555457,32:1024,48:1049601,64:34604033,80:0,96:1,112:34603009,128:33555456,144:1048577,160:33554433,176:34604032,192:34603008,208:1025,224:1049600,240:33554432,8:34603009,24:0,40:33555457,56:34604032,72:1048576,88:33554433,104:33554432,120:1025,136:1049601,152:33555456,168:34603008,184:1048577,200:1024,216:34604033,232:1,248:1049600,256:33554432,272:1048576,288:33555457,304:34603009,320:1048577,336:33555456,352:34604032,368:1049601,384:1025,400:34604033,416:1049600,432:1,448:0,464:34603008,480:33554433,496:1024,264:1049600,280:33555457,296:34603009,312:1,328:33554432,344:1048576,360:1025,376:34604032,392:33554433,408:34603008,424:0,440:34604033,456:1049601,472:1024,488:33555456,504:1048577},{0:134219808,1:131072,2:134217728,3:32,4:131104,5:134350880,6:134350848,7:2048,8:134348800,9:134219776,10:133120,11:134348832,12:2080,13:0,14:134217760,15:133152,2147483648:2048,2147483649:134350880,2147483650:134219808,2147483651:134217728,2147483652:134348800,2147483653:133120,2147483654:133152,2147483655:32,2147483656:134217760,2147483657:2080,2147483658:131104,2147483659:134350848,2147483660:0,2147483661:134348832,2147483662:134219776,2147483663:131072,16:133152,17:134350848,18:32,19:2048,20:134219776,21:134217760,22:134348832,23:131072,24:0,25:131104,26:134348800,27:134219808,28:134350880,29:133120,30:2080,31:134217728,2147483664:131072,2147483665:2048,2147483666:134348832,2147483667:133152,2147483668:32,2147483669:134348800,2147483670:134217728,2147483671:134219808,2147483672:134350880,2147483673:134217760,2147483674:134219776,2147483675:0,2147483676:133120,2147483677:2080,2147483678:131104,2147483679:134350848}],p=[4160749569,528482304,33030144,2064384,129024,8064,504,2147483679],d=s.DES=c.extend({_doReset:function(){for(var e=this._key,r=e.words,t=[],i=0;56>i;i++){var o=a[i]-1;t[i]=1&r[o>>>5]>>>31-o%32}for(var n=this._subKeys=[],c=0;16>c;c++){for(var s=n[c]=[],h=u[c],i=0;24>i;i++)s[0|i/6]|=t[(f[i]-1+h)%28]<<31-i%6,s[4+(0|i/6)]|=t[28+(f[i+24]-1+h)%28]<<31-i%6;s[0]=s[0]<<1|s[0]>>>31;for(var i=1;7>i;i++)s[i]=s[i]>>>4*(i-1)+3;s[7]=s[7]<<5|s[7]>>>27}for(var p=this._invSubKeys=[],i=0;16>i;i++)p[i]=n[15-i]},encryptBlock:function(e,r){this._doCryptBlock(e,r,this._subKeys)},decryptBlock:function(e,r){this._doCryptBlock(e,r,this._invSubKeys)},_doCryptBlock:function(e,i,o){this._lBlock=e[i],this._rBlock=e[i+1],r.call(this,4,252645135),r.call(this,16,65535),t.call(this,2,858993459),t.call(this,8,16711935),r.call(this,1,1431655765);for(var n=0;16>n;n++){for(var c=o[n],s=this._lBlock,a=this._rBlock,f=0,u=0;8>u;u++)f|=h[u][((a^c[u])&p[u])>>>0];this._lBlock=a,this._rBlock=s^f}var d=this._lBlock;this._lBlock=this._rBlock,this._rBlock=d,r.call(this,1,1431655765),t.call(this,8,16711935),t.call(this,2,858993459),r.call(this,16,65535),r.call(this,4,252645135),e[i]=this._lBlock,e[i+1]=this._rBlock},keySize:2,ivSize:2,blockSize:2});i.DES=c._createHelper(d);var l=s.TripleDES=c.extend({_doReset:function(){var e=this._key,r=e.words;this._des1=d.createEncryptor(n.create(r.slice(0,2))),this._des2=d.createEncryptor(n.create(r.slice(2,4))),this._des3=d.createEncryptor(n.create(r.slice(4,6)))},encryptBlock:function(e,r){this._des1.encryptBlock(e,r),this._des2.decryptBlock(e,r),this._des3.encryptBlock(e,r)},decryptBlock:function(e,r){this._des3.decryptBlock(e,r),this._des2.encryptBlock(e,r),this._des1.decryptBlock(e,r)},keySize:6,ivSize:2,blockSize:2});i.TripleDES=c._createHelper(l)}(),e.TripleDES});
},{"./cipher-core":8,"./core":9,"./enc-base64":10,"./evpkdf":12,"./md5":17}],40:[function(require,module,exports){
(function(e,r){"object"==typeof exports?module.exports=exports=r(require("./core")):"function"==typeof define&&define.amd?define(["./core"],r):r(e.CryptoJS)})(this,function(e){return function(r){var t=e,i=t.lib,n=i.Base,o=i.WordArray,c=t.x64={};c.Word=n.extend({init:function(e,r){this.high=e,this.low=r}}),c.WordArray=n.extend({init:function(e,t){e=this.words=e||[],this.sigBytes=t!=r?t:8*e.length},toX32:function(){for(var e=this.words,r=e.length,t=[],i=0;r>i;i++){var n=e[i];t.push(n.high),t.push(n.low)}return o.create(t,this.sigBytes)},clone:function(){for(var e=n.clone.call(this),r=e.words=this.words.slice(0),t=r.length,i=0;t>i;i++)r[i]=r[i].clone();return e}})}(),e});
},{"./core":9}],41:[function(require,module,exports){
/** @license MIT License (c) copyright 2013 original author or authors */

/**
 * function.js
 *
 * Collection of helper functions for wrapping and executing 'traditional'
 * synchronous functions in a promise interface.
 *
 * @author brian@hovercraftstudios.com
 * @contributor renato.riccieri@gmail.com
 */

(function(define) {
define(function(require) {

	var when, slice;

	when = require('./when');
	slice = [].slice;

	return {
		apply: apply,
		call: call,
		lift: lift,
		bind: lift, // DEPRECATED alias for lift
		compose: compose
	};

	/**
	 * Takes a function and an optional array of arguments (that might be promises),
	 * and calls the function. The return value is a promise whose resolution
	 * depends on the value returned by the function.
	 *
	 * @example
	 *    function onlySmallNumbers(n) {
	 *		if(n < 10) {
	 *			return n + 10;
	 *		} else {
	 *			throw new Error("Calculation failed");
	 *		}
	 *	}
	 *
	 * // Logs '15'
	 * func.apply(onlySmallNumbers, [5]).then(console.log, console.error);
	 *
	 * // Logs 'Calculation failed'
	 * func.apply(onlySmallNumbers, [15]).then(console.log, console.error);
	 *
	 * @param {function} func function to be called
	 * @param {Array} [args] array of arguments to func
	 * @returns {Promise} promise for the return value of func
	 */
	function apply(func, promisedArgs) {
		return _apply(func, this, promisedArgs);
	}

	/**
	 * Apply helper that allows specifying thisArg
	 * @private
	 */
	function _apply(func, thisArg, promisedArgs) {
		return when.all(promisedArgs || [], function(args) {
			return func.apply(thisArg, args);
		});
	}
	/**
	 * Has the same behavior that {@link apply} has, with the difference that the
	 * arguments to the function are provided individually, while {@link apply} accepts
	 * a single array.
	 *
	 * @example
	 *    function sumSmallNumbers(x, y) {
	 *		var result = x + y;
	 *		if(result < 10) {
	 *			return result;
	 *		} else {
	 *			throw new Error("Calculation failed");
	 *		}
	 *	}
	 *
	 * // Logs '5'
	 * func.apply(sumSmallNumbers, 2, 3).then(console.log, console.error);
	 *
	 * // Logs 'Calculation failed'
	 * func.apply(sumSmallNumbers, 5, 10).then(console.log, console.error);
	 *
	 * @param {function} func function to be called
	 * @param {...*} [args] arguments that will be forwarded to the function
	 * @returns {Promise} promise for the return value of func
	 */
	function call(func /*, args... */) {
		return _apply(func, this, slice.call(arguments, 1));
	}

	/**
	 * Takes a 'regular' function and returns a version of that function that
	 * returns a promise instead of a plain value, and handles thrown errors by
	 * returning a rejected promise. Also accepts a list of arguments to be
	 * prepended to the new function, as does Function.prototype.bind.
	 *
	 * The resulting function is promise-aware, in the sense that it accepts
	 * promise arguments, and waits for their resolution.
	 *
	 * @example
	 *    function mayThrowError(n) {
	 *		if(n % 2 === 1) { // Normally this wouldn't be so deterministic :)
	 *			throw new Error("I don't like odd numbers");
	 *		} else {
	 *			return n;
	 *		}
	 *	}
	 *
	 *    var lifted = fn.lift(mayThrowError);
	 *
	 *    // Logs "I don't like odd numbers"
	 *    lifted(1).then(console.log, console.error);
	 *
	 *    // Logs '6'
	 *    lifted(6).then(console.log, console.error);
	 *
	 * @example
	 *    function sumTwoNumbers(x, y) {
	 *		return x + y;
	 *	}
	 *
	 *    var sumWithFive = fn.lifted(sumTwoNumbers, 5);
	 *
	 *    // Logs '15'
	 *    sumWithFive(10).then(console.log, console.error);
	 *
	 *    @param {Function} func function to be bound
	 *    @param {...*} [args] arguments to be prepended for the new function
	 *    @returns {Function} a promise-returning function
	 */
	function lift(func /*, args... */) {
		var args = slice.call(arguments, 1);
		return function() {
			return _apply(func, this, args.concat(slice.call(arguments)));
		};
	}

	/**
	 * Composes multiple functions by piping their return values. It is
	 * transparent to whether the functions return 'regular' values or promises:
	 * the piped argument is always a resolved value. If one of the functions
	 * throws or returns a rejected promise, the composed promise will be also
	 * rejected.
	 *
	 * The arguments (or promises to arguments) given to the returned function (if
	 * any), are passed directly to the first function on the 'pipeline'.
	 *
	 * @example
	 *    function getHowMuchWeWillDestroy(parameter) {
	 *		// Makes some calculations to find out which items the modification the user
	 *		// wants will destroy. Returns a number
	 *	}
	 *
	 *    function getUserConfirmation(itemsCount) {
	 *		// Return a resolved promise if the user confirms the destruction,
	 *		// and rejects it otherwise
	 *	}
	 *
	 *    function saveModifications() {
	 *		// Makes ajax to save modifications on the server, returning a
	 *		// promise.
	 *	}
	 *
	 *    function showNotification() {
	 *		// Notifies that the modification was successful
	 *	}
	 *
	 *    // Composes the whole process into one function that returns a promise
	 *    var wholeProcess = func.compose(getHowMuchWeWillDestroy,
	 *                                   getUserConfirmation,
	 *                                   saveModifications,
	 *                                   showNotification);
	 *
	 *    // Which is equivalent to
	 *    var wholeProcess = function(parameter) {
	 *		return fn.call(getHowMuchWeWillDestroy, parameter)
	 *			.then(getUserConfirmation)
	 *			.then(saveModifications)
	 *			.then(showNotification);
	 *	}
	 *
	 * @param {Function} f the function to which the arguments will be passed
	 * @param {...Function} [funcs] functions that will be composed, in order
	 * @returns {Function} a promise-returning composition of the functions
	 */
	function compose(f /*, funcs... */) {
		var funcs = slice.call(arguments, 1);

		return function() {
			var thisArg, args, firstPromise;

			thisArg = this;
			args = slice.call(arguments);
			firstPromise = _apply(f, thisArg, args);

			return when.reduce(funcs, function(arg, func) {
				return func.call(thisArg, arg);
			}, firstPromise);
		};
	}
});

})(
	typeof define === 'function' && define.amd ? define : function (factory) { module.exports = factory(require); }
	// Boilerplate for AMD and Node
);



},{"./when":42}],42:[function(require,module,exports){
var process=require("__browserify_process");/** @license MIT License (c) copyright 2011-2013 original author or authors */

/**
 * A lightweight CommonJS Promises/A and when() implementation
 * when is part of the cujo.js family of libraries (http://cujojs.com/)
 *
 * Licensed under the MIT License at:
 * http://www.opensource.org/licenses/mit-license.php
 *
 * @author Brian Cavalier
 * @author John Hann
 * @version 2.8.0
 */
(function(define) { 'use strict';
define(function (require) {

	// Public API

	when.promise   = promise;    // Create a pending promise
	when.resolve   = resolve;    // Create a resolved promise
	when.reject    = reject;     // Create a rejected promise
	when.defer     = defer;      // Create a {promise, resolver} pair

	when.join      = join;       // Join 2 or more promises

	when.all       = all;        // Resolve a list of promises
	when.map       = map;        // Array.map() for promises
	when.reduce    = reduce;     // Array.reduce() for promises
	when.settle    = settle;     // Settle a list of promises

	when.any       = any;        // One-winner race
	when.some      = some;       // Multi-winner race

	when.isPromise = isPromiseLike;  // DEPRECATED: use isPromiseLike
	when.isPromiseLike = isPromiseLike; // Is something promise-like, aka thenable

	/**
	 * Register an observer for a promise or immediate value.
	 *
	 * @param {*} promiseOrValue
	 * @param {function?} [onFulfilled] callback to be called when promiseOrValue is
	 *   successfully fulfilled.  If promiseOrValue is an immediate value, callback
	 *   will be invoked immediately.
	 * @param {function?} [onRejected] callback to be called when promiseOrValue is
	 *   rejected.
	 * @param {function?} [onProgress] callback to be called when progress updates
	 *   are issued for promiseOrValue.
	 * @returns {Promise} a new {@link Promise} that will complete with the return
	 *   value of callback or errback or the completion value of promiseOrValue if
	 *   callback and/or errback is not supplied.
	 */
	function when(promiseOrValue, onFulfilled, onRejected, onProgress) {
		// Get a trusted promise for the input promiseOrValue, and then
		// register promise handlers
		return cast(promiseOrValue).then(onFulfilled, onRejected, onProgress);
	}

	/**
	 * Creates a new promise whose fate is determined by resolver.
	 * @param {function} resolver function(resolve, reject, notify)
	 * @returns {Promise} promise whose fate is determine by resolver
	 */
	function promise(resolver) {
		return new Promise(resolver,
			monitorApi.PromiseStatus && monitorApi.PromiseStatus());
	}

	/**
	 * Trusted Promise constructor.  A Promise created from this constructor is
	 * a trusted when.js promise.  Any other duck-typed promise is considered
	 * untrusted.
	 * @constructor
	 * @returns {Promise} promise whose fate is determine by resolver
	 * @name Promise
	 */
	function Promise(resolver, status) {
		var self, value, consumers = [];

		self = this;
		this._status = status;
		this.inspect = inspect;
		this._when = _when;

		// Call the provider resolver to seal the promise's fate
		try {
			resolver(promiseResolve, promiseReject, promiseNotify);
		} catch(e) {
			promiseReject(e);
		}

		/**
		 * Returns a snapshot of this promise's current status at the instant of call
		 * @returns {{state:String}}
		 */
		function inspect() {
			return value ? value.inspect() : toPendingState();
		}

		/**
		 * Private message delivery. Queues and delivers messages to
		 * the promise's ultimate fulfillment value or rejection reason.
		 * @private
		 */
		function _when(resolve, notify, onFulfilled, onRejected, onProgress) {
			consumers ? consumers.push(deliver) : enqueue(function() { deliver(value); });

			function deliver(p) {
				p._when(resolve, notify, onFulfilled, onRejected, onProgress);
			}
		}

		/**
		 * Transition from pre-resolution state to post-resolution state, notifying
		 * all listeners of the ultimate fulfillment or rejection
		 * @param {*} val resolution value
		 */
		function promiseResolve(val) {
			if(!consumers) {
				return;
			}

			var queue = consumers;
			consumers = undef;

			value = coerce(self, val);
			enqueue(function () {
				if(status) {
					updateStatus(value, status);
				}
				runHandlers(queue, value);
			});
		}

		/**
		 * Reject this promise with the supplied reason, which will be used verbatim.
		 * @param {*} reason reason for the rejection
		 */
		function promiseReject(reason) {
			promiseResolve(new RejectedPromise(reason));
		}

		/**
		 * Issue a progress event, notifying all progress listeners
		 * @param {*} update progress event payload to pass to all listeners
		 */
		function promiseNotify(update) {
			if(consumers) {
				var queue = consumers;
				enqueue(function () {
					runHandlers(queue, new ProgressingPromise(update));
				});
			}
		}
	}

	promisePrototype = Promise.prototype;

	/**
	 * Register handlers for this promise.
	 * @param [onFulfilled] {Function} fulfillment handler
	 * @param [onRejected] {Function} rejection handler
	 * @param [onProgress] {Function} progress handler
	 * @return {Promise} new Promise
	 */
	promisePrototype.then = function(onFulfilled, onRejected, onProgress) {
		var self = this;

		return new Promise(function(resolve, reject, notify) {
			self._when(resolve, notify, onFulfilled, onRejected, onProgress);
		}, this._status && this._status.observed());
	};

	/**
	 * Register a rejection handler.  Shortcut for .then(undefined, onRejected)
	 * @param {function?} onRejected
	 * @return {Promise}
	 */
	promisePrototype['catch'] = promisePrototype.otherwise = function(onRejected) {
		return this.then(undef, onRejected);
	};

	/**
	 * Ensures that onFulfilledOrRejected will be called regardless of whether
	 * this promise is fulfilled or rejected.  onFulfilledOrRejected WILL NOT
	 * receive the promises' value or reason.  Any returned value will be disregarded.
	 * onFulfilledOrRejected may throw or return a rejected promise to signal
	 * an additional error.
	 * @param {function} onFulfilledOrRejected handler to be called regardless of
	 *  fulfillment or rejection
	 * @returns {Promise}
	 */
	promisePrototype['finally'] = promisePrototype.ensure = function(onFulfilledOrRejected) {
		return typeof onFulfilledOrRejected === 'function'
			? this.then(injectHandler, injectHandler)['yield'](this)
			: this;

		function injectHandler() {
			return resolve(onFulfilledOrRejected());
		}
	};

	/**
	 * Terminate a promise chain by handling the ultimate fulfillment value or
	 * rejection reason, and assuming responsibility for all errors.  if an
	 * error propagates out of handleResult or handleFatalError, it will be
	 * rethrown to the host, resulting in a loud stack track on most platforms
	 * and a crash on some.
	 * @param {function?} handleResult
	 * @param {function?} handleError
	 * @returns {undefined}
	 */
	promisePrototype.done = function(handleResult, handleError) {
		this.then(handleResult, handleError)['catch'](crash);
	};

	/**
	 * Shortcut for .then(function() { return value; })
	 * @param  {*} value
	 * @return {Promise} a promise that:
	 *  - is fulfilled if value is not a promise, or
	 *  - if value is a promise, will fulfill with its value, or reject
	 *    with its reason.
	 */
	promisePrototype['yield'] = function(value) {
		return this.then(function() {
			return value;
		});
	};

	/**
	 * Runs a side effect when this promise fulfills, without changing the
	 * fulfillment value.
	 * @param {function} onFulfilledSideEffect
	 * @returns {Promise}
	 */
	promisePrototype.tap = function(onFulfilledSideEffect) {
		return this.then(onFulfilledSideEffect)['yield'](this);
	};

	/**
	 * Assumes that this promise will fulfill with an array, and arranges
	 * for the onFulfilled to be called with the array as its argument list
	 * i.e. onFulfilled.apply(undefined, array).
	 * @param {function} onFulfilled function to receive spread arguments
	 * @return {Promise}
	 */
	promisePrototype.spread = function(onFulfilled) {
		return this.then(function(array) {
			// array may contain promises, so resolve its contents.
			return all(array, function(array) {
				return onFulfilled.apply(undef, array);
			});
		});
	};

	/**
	 * Shortcut for .then(onFulfilledOrRejected, onFulfilledOrRejected)
	 * @deprecated
	 */
	promisePrototype.always = function(onFulfilledOrRejected, onProgress) {
		return this.then(onFulfilledOrRejected, onFulfilledOrRejected, onProgress);
	};

	/**
	 * Casts x to a trusted promise. If x is already a trusted promise, it is
	 * returned, otherwise a new trusted Promise which follows x is returned.
	 * @param {*} x
	 * @returns {Promise}
	 */
	function cast(x) {
		return x instanceof Promise ? x : resolve(x);
	}

	/**
	 * Returns a resolved promise. The returned promise will be
	 *  - fulfilled with promiseOrValue if it is a value, or
	 *  - if promiseOrValue is a promise
	 *    - fulfilled with promiseOrValue's value after it is fulfilled
	 *    - rejected with promiseOrValue's reason after it is rejected
	 * In contract to cast(x), this always creates a new Promise
	 * @param  {*} x
	 * @return {Promise}
	 */
	function resolve(x) {
		return promise(function(resolve) {
			resolve(x);
		});
	}

	/**
	 * Returns a rejected promise for the supplied promiseOrValue.  The returned
	 * promise will be rejected with:
	 * - promiseOrValue, if it is a value, or
	 * - if promiseOrValue is a promise
	 *   - promiseOrValue's value after it is fulfilled
	 *   - promiseOrValue's reason after it is rejected
	 * @deprecated The behavior of when.reject in 3.0 will be to reject
	 * with x VERBATIM
	 * @param {*} x the rejected value of the returned promise
	 * @return {Promise} rejected promise
	 */
	function reject(x) {
		return when(x, function(e) {
			return new RejectedPromise(e);
		});
	}

	/**
	 * Creates a {promise, resolver} pair, either or both of which
	 * may be given out safely to consumers.
	 * The resolver has resolve, reject, and progress.  The promise
	 * has then plus extended promise API.
	 *
	 * @return {{
	 * promise: Promise,
	 * resolve: function:Promise,
	 * reject: function:Promise,
	 * notify: function:Promise
	 * resolver: {
	 *	resolve: function:Promise,
	 *	reject: function:Promise,
	 *	notify: function:Promise
	 * }}}
	 */
	function defer() {
		var deferred, pending, resolved;

		// Optimize object shape
		deferred = {
			promise: undef, resolve: undef, reject: undef, notify: undef,
			resolver: { resolve: undef, reject: undef, notify: undef }
		};

		deferred.promise = pending = promise(makeDeferred);

		return deferred;

		function makeDeferred(resolvePending, rejectPending, notifyPending) {
			deferred.resolve = deferred.resolver.resolve = function(value) {
				if(resolved) {
					return resolve(value);
				}
				resolved = true;
				resolvePending(value);
				return pending;
			};

			deferred.reject  = deferred.resolver.reject  = function(reason) {
				if(resolved) {
					return resolve(new RejectedPromise(reason));
				}
				resolved = true;
				rejectPending(reason);
				return pending;
			};

			deferred.notify  = deferred.resolver.notify  = function(update) {
				notifyPending(update);
				return update;
			};
		}
	}

	/**
	 * Run a queue of functions as quickly as possible, passing
	 * value to each.
	 */
	function runHandlers(queue, value) {
		for (var i = 0; i < queue.length; i++) {
			queue[i](value);
		}
	}

	/**
	 * Coerces x to a trusted Promise
	 * @param {*} x thing to coerce
	 * @returns {*} Guaranteed to return a trusted Promise.  If x
	 *   is trusted, returns x, otherwise, returns a new, trusted, already-resolved
	 *   Promise whose resolution value is:
	 *   * the resolution value of x if it's a foreign promise, or
	 *   * x if it's a value
	 */
	function coerce(self, x) {
		if (x === self) {
			return new RejectedPromise(new TypeError());
		}

		if (x instanceof Promise) {
			return x;
		}

		try {
			var untrustedThen = x === Object(x) && x.then;

			return typeof untrustedThen === 'function'
				? assimilate(untrustedThen, x)
				: new FulfilledPromise(x);
		} catch(e) {
			return new RejectedPromise(e);
		}
	}

	/**
	 * Safely assimilates a foreign thenable by wrapping it in a trusted promise
	 * @param {function} untrustedThen x's then() method
	 * @param {object|function} x thenable
	 * @returns {Promise}
	 */
	function assimilate(untrustedThen, x) {
		return promise(function (resolve, reject) {
			enqueue(function() {
				try {
					fcall(untrustedThen, x, resolve, reject);
				} catch(e) {
					reject(e);
				}
			});
		});
	}

	makePromisePrototype = Object.create ||
		function(o) {
			function PromisePrototype() {}
			PromisePrototype.prototype = o;
			return new PromisePrototype();
		};

	/**
	 * Creates a fulfilled, local promise as a proxy for a value
	 * NOTE: must never be exposed
	 * @private
	 * @param {*} value fulfillment value
	 * @returns {Promise}
	 */
	function FulfilledPromise(value) {
		this.value = value;
	}

	FulfilledPromise.prototype = makePromisePrototype(promisePrototype);

	FulfilledPromise.prototype.inspect = function() {
		return toFulfilledState(this.value);
	};

	FulfilledPromise.prototype._when = function(resolve, _, onFulfilled) {
		try {
			resolve(typeof onFulfilled === 'function' ? onFulfilled(this.value) : this.value);
		} catch(e) {
			resolve(new RejectedPromise(e));
		}
	};

	/**
	 * Creates a rejected, local promise as a proxy for a value
	 * NOTE: must never be exposed
	 * @private
	 * @param {*} reason rejection reason
	 * @returns {Promise}
	 */
	function RejectedPromise(reason) {
		this.value = reason;
	}

	RejectedPromise.prototype = makePromisePrototype(promisePrototype);

	RejectedPromise.prototype.inspect = function() {
		return toRejectedState(this.value);
	};

	RejectedPromise.prototype._when = function(resolve, _, __, onRejected) {
		try {
			resolve(typeof onRejected === 'function' ? onRejected(this.value) : this);
		} catch(e) {
			resolve(new RejectedPromise(e));
		}
	};

	/**
	 * Create a progress promise with the supplied update.
	 * @private
	 * @param {*} value progress update value
	 * @return {Promise} progress promise
	 */
	function ProgressingPromise(value) {
		this.value = value;
	}

	ProgressingPromise.prototype = makePromisePrototype(promisePrototype);

	ProgressingPromise.prototype._when = function(_, notify, f, r, u) {
		try {
			notify(typeof u === 'function' ? u(this.value) : this.value);
		} catch(e) {
			notify(e);
		}
	};

	/**
	 * Update a PromiseStatus monitor object with the outcome
	 * of the supplied value promise.
	 * @param {Promise} value
	 * @param {PromiseStatus} status
	 */
	function updateStatus(value, status) {
		value.then(statusFulfilled, statusRejected);

		function statusFulfilled() { status.fulfilled(); }
		function statusRejected(r) { status.rejected(r); }
	}

	/**
	 * Determines if x is promise-like, i.e. a thenable object
	 * NOTE: Will return true for *any thenable object*, and isn't truly
	 * safe, since it may attempt to access the `then` property of x (i.e.
	 *  clever/malicious getters may do weird things)
	 * @param {*} x anything
	 * @returns {boolean} true if x is promise-like
	 */
	function isPromiseLike(x) {
		return x && typeof x.then === 'function';
	}

	/**
	 * Initiates a competitive race, returning a promise that will resolve when
	 * howMany of the supplied promisesOrValues have resolved, or will reject when
	 * it becomes impossible for howMany to resolve, for example, when
	 * (promisesOrValues.length - howMany) + 1 input promises reject.
	 *
	 * @param {Array} promisesOrValues array of anything, may contain a mix
	 *      of promises and values
	 * @param howMany {number} number of promisesOrValues to resolve
	 * @param {function?} [onFulfilled] DEPRECATED, use returnedPromise.then()
	 * @param {function?} [onRejected] DEPRECATED, use returnedPromise.then()
	 * @param {function?} [onProgress] DEPRECATED, use returnedPromise.then()
	 * @returns {Promise} promise that will resolve to an array of howMany values that
	 *  resolved first, or will reject with an array of
	 *  (promisesOrValues.length - howMany) + 1 rejection reasons.
	 */
	function some(promisesOrValues, howMany, onFulfilled, onRejected, onProgress) {

		return when(promisesOrValues, function(promisesOrValues) {

			return promise(resolveSome).then(onFulfilled, onRejected, onProgress);

			function resolveSome(resolve, reject, notify) {
				var toResolve, toReject, values, reasons, fulfillOne, rejectOne, len, i;

				len = promisesOrValues.length >>> 0;

				toResolve = Math.max(0, Math.min(howMany, len));
				values = [];

				toReject = (len - toResolve) + 1;
				reasons = [];

				// No items in the input, resolve immediately
				if (!toResolve) {
					resolve(values);

				} else {
					rejectOne = function(reason) {
						reasons.push(reason);
						if(!--toReject) {
							fulfillOne = rejectOne = identity;
							reject(reasons);
						}
					};

					fulfillOne = function(val) {
						// This orders the values based on promise resolution order
						values.push(val);
						if (!--toResolve) {
							fulfillOne = rejectOne = identity;
							resolve(values);
						}
					};

					for(i = 0; i < len; ++i) {
						if(i in promisesOrValues) {
							when(promisesOrValues[i], fulfiller, rejecter, notify);
						}
					}
				}

				function rejecter(reason) {
					rejectOne(reason);
				}

				function fulfiller(val) {
					fulfillOne(val);
				}
			}
		});
	}

	/**
	 * Initiates a competitive race, returning a promise that will resolve when
	 * any one of the supplied promisesOrValues has resolved or will reject when
	 * *all* promisesOrValues have rejected.
	 *
	 * @param {Array|Promise} promisesOrValues array of anything, may contain a mix
	 *      of {@link Promise}s and values
	 * @param {function?} [onFulfilled] DEPRECATED, use returnedPromise.then()
	 * @param {function?} [onRejected] DEPRECATED, use returnedPromise.then()
	 * @param {function?} [onProgress] DEPRECATED, use returnedPromise.then()
	 * @returns {Promise} promise that will resolve to the value that resolved first, or
	 * will reject with an array of all rejected inputs.
	 */
	function any(promisesOrValues, onFulfilled, onRejected, onProgress) {

		function unwrapSingleResult(val) {
			return onFulfilled ? onFulfilled(val[0]) : val[0];
		}

		return some(promisesOrValues, 1, unwrapSingleResult, onRejected, onProgress);
	}

	/**
	 * Return a promise that will resolve only once all the supplied promisesOrValues
	 * have resolved. The resolution value of the returned promise will be an array
	 * containing the resolution values of each of the promisesOrValues.
	 * @memberOf when
	 *
	 * @param {Array|Promise} promisesOrValues array of anything, may contain a mix
	 *      of {@link Promise}s and values
	 * @param {function?} [onFulfilled] DEPRECATED, use returnedPromise.then()
	 * @param {function?} [onRejected] DEPRECATED, use returnedPromise.then()
	 * @param {function?} [onProgress] DEPRECATED, use returnedPromise.then()
	 * @returns {Promise}
	 */
	function all(promisesOrValues, onFulfilled, onRejected, onProgress) {
		return _map(promisesOrValues, identity).then(onFulfilled, onRejected, onProgress);
	}

	/**
	 * Joins multiple promises into a single returned promise.
	 * @return {Promise} a promise that will fulfill when *all* the input promises
	 * have fulfilled, or will reject when *any one* of the input promises rejects.
	 */
	function join(/* ...promises */) {
		return _map(arguments, identity);
	}

	/**
	 * Settles all input promises such that they are guaranteed not to
	 * be pending once the returned promise fulfills. The returned promise
	 * will always fulfill, except in the case where `array` is a promise
	 * that rejects.
	 * @param {Array|Promise} array or promise for array of promises to settle
	 * @returns {Promise} promise that always fulfills with an array of
	 *  outcome snapshots for each input promise.
	 */
	function settle(array) {
		return _map(array, toFulfilledState, toRejectedState);
	}

	/**
	 * Promise-aware array map function, similar to `Array.prototype.map()`,
	 * but input array may contain promises or values.
	 * @param {Array|Promise} array array of anything, may contain promises and values
	 * @param {function} mapFunc map function which may return a promise or value
	 * @returns {Promise} promise that will fulfill with an array of mapped values
	 *  or reject if any input promise rejects.
	 */
	function map(array, mapFunc) {
		return _map(array, mapFunc);
	}

	/**
	 * Internal map that allows a fallback to handle rejections
	 * @param {Array|Promise} array array of anything, may contain promises and values
	 * @param {function} mapFunc map function which may return a promise or value
	 * @param {function?} fallback function to handle rejected promises
	 * @returns {Promise} promise that will fulfill with an array of mapped values
	 *  or reject if any input promise rejects.
	 */
	function _map(array, mapFunc, fallback) {
		return when(array, function(array) {

			return new Promise(resolveMap);

			function resolveMap(resolve, reject, notify) {
				var results, len, toResolve, i;

				// Since we know the resulting length, we can preallocate the results
				// array to avoid array expansions.
				toResolve = len = array.length >>> 0;
				results = [];

				if(!toResolve) {
					resolve(results);
					return;
				}

				// Since mapFunc may be async, get all invocations of it into flight
				for(i = 0; i < len; i++) {
					if(i in array) {
						resolveOne(array[i], i);
					} else {
						--toResolve;
					}
				}

				function resolveOne(item, i) {
					when(item, mapFunc, fallback).then(function(mapped) {
						results[i] = mapped;

						if(!--toResolve) {
							resolve(results);
						}
					}, reject, notify);
				}
			}
		});
	}

	/**
	 * Traditional reduce function, similar to `Array.prototype.reduce()`, but
	 * input may contain promises and/or values, and reduceFunc
	 * may return either a value or a promise, *and* initialValue may
	 * be a promise for the starting value.
	 *
	 * @param {Array|Promise} promise array or promise for an array of anything,
	 *      may contain a mix of promises and values.
	 * @param {function} reduceFunc reduce function reduce(currentValue, nextValue, index, total),
	 *      where total is the total number of items being reduced, and will be the same
	 *      in each call to reduceFunc.
	 * @returns {Promise} that will resolve to the final reduced value
	 */
	function reduce(promise, reduceFunc /*, initialValue */) {
		var args = fcall(slice, arguments, 1);

		return when(promise, function(array) {
			var total;

			total = array.length;

			// Wrap the supplied reduceFunc with one that handles promises and then
			// delegates to the supplied.
			args[0] = function (current, val, i) {
				return when(current, function (c) {
					return when(val, function (value) {
						return reduceFunc(c, value, i, total);
					});
				});
			};

			return reduceArray.apply(array, args);
		});
	}

	// Snapshot states

	/**
	 * Creates a fulfilled state snapshot
	 * @private
	 * @param {*} x any value
	 * @returns {{state:'fulfilled',value:*}}
	 */
	function toFulfilledState(x) {
		return { state: 'fulfilled', value: x };
	}

	/**
	 * Creates a rejected state snapshot
	 * @private
	 * @param {*} x any reason
	 * @returns {{state:'rejected',reason:*}}
	 */
	function toRejectedState(x) {
		return { state: 'rejected', reason: x };
	}

	/**
	 * Creates a pending state snapshot
	 * @private
	 * @returns {{state:'pending'}}
	 */
	function toPendingState() {
		return { state: 'pending' };
	}

	//
	// Internals, utilities, etc.
	//

	var promisePrototype, makePromisePrototype, reduceArray, slice, fcall, nextTick, handlerQueue,
		funcProto, call, arrayProto, monitorApi,
		capturedSetTimeout, cjsRequire, MutationObs, undef;

	cjsRequire = require;

	//
	// Shared handler queue processing
	//
	// Credit to Twisol (https://github.com/Twisol) for suggesting
	// this type of extensible queue + trampoline approach for
	// next-tick conflation.

	handlerQueue = [];

	/**
	 * Enqueue a task. If the queue is not currently scheduled to be
	 * drained, schedule it.
	 * @param {function} task
	 */
	function enqueue(task) {
		if(handlerQueue.push(task) === 1) {
			nextTick(drainQueue);
		}
	}

	/**
	 * Drain the handler queue entirely, being careful to allow the
	 * queue to be extended while it is being processed, and to continue
	 * processing until it is truly empty.
	 */
	function drainQueue() {
		runHandlers(handlerQueue);
		handlerQueue = [];
	}

	// Allow attaching the monitor to when() if env has no console
	monitorApi = typeof console !== 'undefined' ? console : when;

	// Sniff "best" async scheduling option
	// Prefer process.nextTick or MutationObserver, then check for
	// vertx and finally fall back to setTimeout
	/*global process,document,setTimeout,MutationObserver,WebKitMutationObserver*/
	if (typeof process === 'object' && process.nextTick) {
		nextTick = process.nextTick;
	} else if(MutationObs =
		(typeof MutationObserver === 'function' && MutationObserver) ||
			(typeof WebKitMutationObserver === 'function' && WebKitMutationObserver)) {
		nextTick = (function(document, MutationObserver, drainQueue) {
			var el = document.createElement('div');
			new MutationObserver(drainQueue).observe(el, { attributes: true });

			return function() {
				el.setAttribute('x', 'x');
			};
		}(document, MutationObs, drainQueue));
	} else {
		try {
			// vert.x 1.x || 2.x
			nextTick = cjsRequire('vertx').runOnLoop || cjsRequire('vertx').runOnContext;
		} catch(ignore) {
			// capture setTimeout to avoid being caught by fake timers
			// used in time based tests
			capturedSetTimeout = setTimeout;
			nextTick = function(t) { capturedSetTimeout(t, 0); };
		}
	}

	//
	// Capture/polyfill function and array utils
	//

	// Safe function calls
	funcProto = Function.prototype;
	call = funcProto.call;
	fcall = funcProto.bind
		? call.bind(call)
		: function(f, context) {
			return f.apply(context, slice.call(arguments, 2));
		};

	// Safe array ops
	arrayProto = [];
	slice = arrayProto.slice;

	// ES5 reduce implementation if native not available
	// See: http://es5.github.com/#x15.4.4.21 as there are many
	// specifics and edge cases.  ES5 dictates that reduce.length === 1
	// This implementation deviates from ES5 spec in the following ways:
	// 1. It does not check if reduceFunc is a Callable
	reduceArray = arrayProto.reduce ||
		function(reduceFunc /*, initialValue */) {
			/*jshint maxcomplexity: 7*/
			var arr, args, reduced, len, i;

			i = 0;
			arr = Object(this);
			len = arr.length >>> 0;
			args = arguments;

			// If no initialValue, use first item of array (we know length !== 0 here)
			// and adjust i to start at second item
			if(args.length <= 1) {
				// Skip to the first real element in the array
				for(;;) {
					if(i in arr) {
						reduced = arr[i++];
						break;
					}

					// If we reached the end of the array without finding any real
					// elements, it's a TypeError
					if(++i >= len) {
						throw new TypeError();
					}
				}
			} else {
				// If initialValue provided, use it
				reduced = args[1];
			}

			// Do the actual reduce
			for(;i < len; ++i) {
				if(i in arr) {
					reduced = reduceFunc(reduced, arr[i], i, arr);
				}
			}

			return reduced;
		};

	function identity(x) {
		return x;
	}

	function crash(fatalError) {
		if(typeof monitorApi.reportUnhandled === 'function') {
			monitorApi.reportUnhandled();
		} else {
			enqueue(function() {
				throw fatalError;
			});
		}

		throw fatalError;
	}

	return when;
});
})(typeof define === 'function' && define.amd ? define : function (factory) { module.exports = factory(require); });

},{"__browserify_process":1}],43:[function(require,module,exports){

/**
 * Module dependencies.
 */

var global = (function() { return this; })();

/**
 * WebSocket constructor.
 */

var WebSocket = global.WebSocket || global.MozWebSocket;

/**
 * Module exports.
 */

module.exports = WebSocket ? ws : null;

/**
 * WebSocket constructor.
 *
 * The third `opts` options object gets ignored in web browsers, since it's
 * non-standard, and throws a TypeError if passed to the constructor.
 * See: https://github.com/einaros/ws/issues/227
 *
 * @param {String} uri
 * @param {Array} protocols (optional)
 * @param {Object) opts (optional)
 * @api public
 */

function ws(uri, protocols, opts) {
  var instance;
  if (protocols) {
    instance = new WebSocket(uri, protocols);
  } else {
    instance = new WebSocket(uri);
  }
  return instance;
}

if (WebSocket) ws.prototype = WebSocket.prototype;

},{}],44:[function(require,module,exports){
module.exports={
   "name": "autobahn",
   "version": "0.9.1-2",
   "description": "An implementation of The Web Application Messaging Protocol (WAMP).",
   "main": "index.js",
   "scripts": {
      "test": "node test/test3.js"
   },
   "dependencies": {
      "when": ">= 2.8.0",
      "ws": ">= 0.4.31",
      "crypto-js": ">= 3.1.2-2"
   },
   "devDependencies": {
      "browserify": ">= 3.28.1"
   },
   "repository": {
      "type": "git",
      "url": "git://github.com/tavendo/AutobahnJS.git"
   },
   "keywords": [
      "WAMP",
      "WebSocket",
      "RPC",
      "PubSub"
   ],
   "author": "Tavendo GmbH",
   "license": "MIT"
}

},{}]},{},[2])(2)
});
;