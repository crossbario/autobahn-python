# Documentation

The documentation is generated using [Sphinx](http://sphinx.pocoo.org/) and the generated documentation is hosted [here](http://autobahn.ws/python).

## Prerequisites

You will need to have Python and [SCons](http://www.scons.org/) installed. To install the rest of the build dependencies

```sh
make install_deps
```

Then, to get help on available build targets, just type

```sh
make
```

## Cheatsheets

* [How to document your Python docstrings](http://www.ctio.noao.edu/~fraga/pytemplate/pytemplate.html)


## Linking to Python objects

To link to a Autobahn class:

```rst
:py:class:`autobahn.websocket.protocol.WebSocketProtocol`
```

To link to a Python stdlib class:

```rst
:py:class:`zipfile.ZipFile`
```

Or to link to Python 2 or Python 3 specifically:

```rst
:py:class:`zipfile.ZipFile <py2:zipfile.ZipFile>`
:py:class:`zipfile.ZipFile <py3:zipfile.ZipFile>`
```

To link to a Twisted class:

```rst
:tx:`twisted.internet.defer.Deferred`
```
