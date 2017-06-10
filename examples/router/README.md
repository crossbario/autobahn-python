This contains a configuration file in `.crossbar/config.json` to run a local Crossbar instance and serve some of the example content via a Web server.

See [../running-the-examples.md] for more information.

If you get 404 errors on autobahn.min.jgz do this:

   curl --location -o ../autobahn.min.js https://github.com/crossbario/autobahn-js-built/raw/master/autobahn.min.js

... to get the latest autobahn release in the "examples/" directory.
