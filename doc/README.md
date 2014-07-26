# Documentation

The **Autobahn**|Python documentation is generated using [Sphinx](http://sphinx.pocoo.org/) and the generated documentation is hosted [here](http://autobahn.ws/python).


## Generate

You will need to have [SCons](http://scons.org/) installed, plus the following

```sh
pip install taschenmesser
pip install sphinx
pip install sphinx-bootstrap-theme
pip install sphinxcontrib-spelling
pip install repoze.sphinx.autointerface
```

To generate the documentation

```sh
cd doc
scons
```

This will create the documentation under the directory `_build`.


## Test

To build the documentation and start a Web server
```sh
scons test
```

## Clean

To clean up all build artifacts

```sh
scons -uc
```

## Publish

> Note: this section is only relevant for administrators of the [Autobahn web site](http://autobahn.ws/).

To publish to the Autobahn web site ([here](http://autobahn.ws/)), you will need [SCons](http://scons.org/) and [Taschenmesser](https://pypi.python.org/pypi/taschenmesser).

Then do

```sh
scons
```

once to build the docs and then do

```sh
scons publish
```

to publish the docs.
