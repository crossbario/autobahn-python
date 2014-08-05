build:
	scons

build_no_network:
	scons --no_network

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

publish: clean build
	scons publish

doctest:
	PYTHONPATH=../autobahn sphinx-build -b doctest -v . _test

copy_css:
	cp _static/css/page.css ../../AutobahnJS/doc/_static/css/
	cp _static/css/page.css ../../AutobahnAndroid/doc/_static/css/
	cp _static/css/page.css ../../AutobahnCpp/doc/_static/css/
	cp _static/css/page.css ../../AutobahnTestsuite/doc/_static/css/

copy_makefile:
	cp Makefile ../../AutobahnJS/doc/
	cp Makefile ../../AutobahnAndroid/doc/
	cp Makefile ../../AutobahnCpp/doc/
	cp Makefile ../../AutobahnTestsuite/doc/

copy: copy_css copy_makefile

install_deps:
	pip install -U scour
	pip install -U taschenmesser
	#pip install -U scons
	pip install -U sphinx
	pip install -U sphinx-bootstrap-theme
	pip install -U pyenchant
	pip install -U sphinxcontrib-spelling
	pip install -U repoze.sphinx.autointerface

spelling:
	PYTHONPATH=../autobahn sphinx-build -b spelling . _spelling
