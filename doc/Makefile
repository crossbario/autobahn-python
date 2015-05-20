all:
	@echo "Targets:"
	@echo ""
	@echo "  clean             : cleanup build artifacts"
	@echo "  test              : build everything and run locally"
	@echo "  test_no_network   : build everything for no network access and run locally"
	@echo "  publish           : build everything and publish to S3"
	@echo "  copy              : copy over shared files to other AutobahnXXX repos"
	@echo "  install_deps      : install build dependencies"
	@echo "  spelling          : run spell checking"
	@echo "  doctest           : run doctests"
	@echo ""

# need a distribution package for SCons, like "apt-get install scons"
venv:
	virtualenv --system-site-packages --python=python2 venv

# the "python `which scons`" hacks are because I can't get scons
# installed in a virtualenv, and its #! hard-codes to system python
build: install_deps
	./venv/bin/python `which scons`
	./venv/bin/sphinx-build -A cstatic="//tavendo-common-static.s3-eu-west-1.amazonaws.com" -b html . _build

build_no_network: install_deps
	./venv/bin/python `which scons` --no_network
	./venv/bin/sphinx-build -A no_network=1 -D no_network=1 -A cstatic="http://127.0.0.1:8888" -b html . _build

test: build
	python serve.py --root ./_build --silence

test_no_network: build_no_network
	python serve.py --root ./_build --silence

clean:
	rm -rf _build
	rm -rf _build_uploaded
	rm -rf _static/img/gen
	rm -rf _test
	rm -rf _spelling
	rm -rf ./venv

publish: clean build
	scons publish

doctest:
	PYTHONPATH=../autobahn sphinx-build -b doctest -v . _test

copy_makefile:
	cp Makefile ../../AutobahnJS/doc/
	cp Makefile ../../AutobahnAndroid/doc/
	cp Makefile ../../AutobahnCpp/doc/
	cp Makefile ../../AutobahnTestsuite/doc/

copy_gitignore:
	cp .gitignore ../../AutobahnJS/doc/
	cp .gitignore ../../AutobahnAndroid/doc/
	cp .gitignore ../../AutobahnCpp/doc/
	cp .gitignore ../../AutobahnTestsuite/doc/

copy_serve:
	cp serve.py ../../AutobahnJS/doc/
	cp serve.py ../../AutobahnAndroid/doc/
	cp serve.py ../../AutobahnCpp/doc/
	cp serve.py ../../AutobahnTestsuite/doc/

copy_wordlist:
	cp spelling_wordlist.txt ../../AutobahnJS/doc/
	cp spelling_wordlist.txt ../../AutobahnAndroid/doc/
	cp spelling_wordlist.txt ../../AutobahnCpp/doc/
	cp spelling_wordlist.txt ../../AutobahnTestsuite/doc/

# copy_readme:
# 	cp README.md ../../AutobahnJS/doc/
# 	cp README.md ../../AutobahnAndroid/doc/
# 	cp README.md ../../AutobahnCpp/doc/
# 	cp README.md ../../AutobahnTestsuite/doc/

copy: copy_makefile copy_gitignore copy_serve

install_deps: venv
	./venv/bin/pip install -U scour
	./venv/bin/pip install -U taschenmesser
	./venv/bin/pip install -U sphinx
	./venv/bin/pip install -U sphinx-bootstrap-theme
	./venv/bin/pip install -U pyenchant
	./venv/bin/pip install -U sphinxcontrib-spelling
	./venv/bin/pip install -U repoze.sphinx.autointerface
	./venv/bin/pip install -e ../[twisted,asyncio]

spelling:
	PYTHONPATH=../autobahn sphinx-build -b spelling . _spelling
