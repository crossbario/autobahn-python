WebSocket Authentication with Mozilla Persona
=============================================

This example shows how to authenticate WebSocket connections using [Mozilla Persona](http://www.mozilla.org/en-US/persona/) and HTTP Cookies. The example works with purely static Web pages and WebSocket only.

Tested with:

 * Firefox 27
 * Chrome 33
 * IE11

Note: On IE11, using `localhost` as URL [does NOT work](https://groups.google.com/d/msg/mozilla.dev.identity/keEkVpvfLA8/2WIu7Q1mW10J). You must use `127.0.0.1` instead.

References:

* [Mozilla Persona Developer Site](https://developer.mozilla.org/en-US/Persona)


Running
-------

Run the server by doing

    python server.py

and open

    http://localhost:8080/

in your browser.

Here is the log output produced (on server) for a successful login:

    $ python server.py
    2014-03-11 12:20:05+0100 [-] Log opened.
    2014-03-11 12:20:05+0100 [-] Running Autobahn|Python 0.8.4-3
    2014-03-11 12:20:05+0100 [-] Site starting on 8080
    2014-03-11 12:20:05+0100 [-] Starting factory <twisted.web.server.Site instance at 0x038113C8>
    2014-03-11 12:20:23+0100 [HTTPChannel,1,127.0.0.1] Setting new cookie: 82vrA1drjZ_9lcBv
    2014-03-11 12:20:36+0100 [HTTPChannel,1,127.0.0.1] Starting factory <HTTPClientFactory: https://verifier.login.persona.o
    rg/verify>
    2014-03-11 12:20:36+0100 [HTTPChannel,1,127.0.0.1] Authentication request sent.
    2014-03-11 12:20:37+0100 [HTTPPageGetter (TLSMemoryBIOProtocol),client] Authenticated user tobias.oberstein@gmail.com
    2014-03-11 12:20:37+0100 [HTTPPageGetter (TLSMemoryBIOProtocol),client] Stopping factory <HTTPClientFactory: https://verifier.login.persona.org/verify>
    ...

