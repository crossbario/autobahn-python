# Autobahn|Python Documentation

The **Autobahn**|Python reference documentation is generated using [Sphinx](http://sphinx.pocoo.org/) and available [online](http://autobahn.ws/python/reference).

To generate the documentation yourself you will need to have **Autobahn**|Python installed locally plus install Sphinx:

	pip install sphinx
    pip install sphinx_rtd_theme
    pip install sphinxcontrib-spelling
    pip install repoze.sphinx.autointerface

and then

	cd doc
	sphinx-build -b html . _html

This will create the documentation under

	_html


## Publishing

> Note: this section is only relevant for administrators of the [Autobahn web site](http://autobahn.ws/).

To publish to the Autobahn web site ([here](http://autobahn.ws/python/reference/)), you will need [SCons](http://scons.org/) and [Taschenmesser](https://pypi.python.org/pypi/taschenmesser).

Then do

	scons

to build the docs and

	scons publish

to build and publish the docs and

	scons -uc

to cleanup.