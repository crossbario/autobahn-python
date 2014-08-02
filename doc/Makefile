build:
	scons

test: build
	python serve.py --root ./_build --silence

clean:
	rm -rf _build
	rm -rf _build_uploaded
	rm -rf _static/img/gen

publish: clean build
	scons publish

doctest:
	PYTHONPATH=../autobahn sphinx-build -b doctest -v . _test
