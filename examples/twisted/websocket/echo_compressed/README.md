WebSocket Echo Server and Client
================================

This example demonstrates how to activate and use the WebSocket compression extension ([`permessage-deflate`](http://tools.ietf.org/html/draft-ietf-hybi-permessage-compression-09)).

Running
-------

Run the server by doing

    python server.py

and open

    http://localhost:8080/

in your browser.

> Note: Currently (06/04/2013), the only browsers implementing WebSocket `permessage-deflate` are [Chrome Canary](https://www.google.com/intl/en/chrome/browser/canary.html) and [Chromium (Dev Channel)](http://www.chromium.org/getting-involved/dev-channel).
> To enable, go to `chrome://flags/` and enable the "experimental WebSocket implementation".

To run the Python client, do

    python client.py ws://127.0.0.1:9000


Advanced Usage
--------------

AutobahnPython supports fine-grained control over which compression offers a client makes and exactly which offers a server accepts with which settings.

See `server_advanced.py` and `client_advanced.py`.

Besides `permessage-deflate`, AutobahnPython also supports

 * `permessage-bzip2`
 * `permessage-snappy`

> Note: Those compression extensions are currently entirely non-standard, there isn't even a RFC draft for those.
> 

For `permessage-snappy`, you will need the [Snappy](http://code.google.com/p/snappy/) compression library and Python [wrapper](http://github.com/andrix/python-snappy) installed.

On Windows, you can get a prebuilt binary from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/).

On Linux/Debian, you can install it by doing:

    sudo apt-get install libsnappy-dev
    easy_install -U python-snappy

