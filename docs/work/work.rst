



There are many more examples showing options and advanced features:

* :doc:`WebSocket Examples <websocket/examples>`.
* :doc:`WAMP Examples <wamp/examples>`.


.. note::

   * WAMP application components can be run in servers and clients without any modification to your component class.

   * `AutobahnJS`_ allows you to write WAMP application components in JavaScript which run in browsers and Nodejs. Here is how above example `looks like <https://github.com/crossbario/autobahn-js/#show-me-some-code>`_ in JavaScript.


.. note::

   We will refer to |Ab| simply by **Autobahn** when it is clear from the context
   which Autobahn subproject library is meant. In this documentation, this
   is |Ab| almost always.



WAMP implements `two messaging patterns on top of WebSocket <http://wamp.ws/why/>`_:

* **Publish & Subscribe**: *Publishers* publish events to a topic, and *subscribers* to the topic receive these events. A *router* brokers these events.
* **Remote Procedure Calls**: A *callee* registers a remote procedure with a *router*. A *caller* makes a call for that procedure to the *router*. The *router* deals the call to the *callee* and returns the result to the *caller*.

Basic *router* functionality is provided by |ab|.

WAMP is ideal for distributed, multi-client and server applications, such as multi-user database-drive business applications, sensor networks (IoT), instant messaging or MMOGs (massively multi-player online games) .

WAMP enables application architectures with application code distributed freely across processes and devices according to functional aspects. Since WAMP implementations exist for multiple languages, WAMP applications can be polyglot. Application components can be implemented in a language and run on a device which best fit the particular use case.
