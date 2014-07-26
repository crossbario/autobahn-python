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

Publishing requires a **2 step process**.

**First** do

```sh
scons
```

to build the docs and **second** do

```sh
scons publish
```

to actually publish the docs.
