build:
	scons

test: build
	python serve.py --root ./_build --silence

clean:
	rm -rf _build
	rm -rf _build_uploaded
	rm -rf _static/img/gen
	rm -rf _test

publish: clean build
	scons publish

doctest:
	PYTHONPATH=../autobahn sphinx-build -b doctest -v . _test


copy_css:
	cp _static/css/page.css ../../AutobahnJS/doc/_static/css
	cp _static/css/page.css ../../AutobahnAndroid/doc/_static/css
	cp _static/css/page.css ../../AutobahnCpp/doc/_static/css
	cp _static/css/page.css ../../AutobahnTestsuite/doc/_static/css

