all:
	@echo "Targets:"
	@echo ""
	@echo "   install          Local install"
	@echo "   clean            Cleanup"
	@echo "   build            Clean build"
	@echo "   deploy_release   Clean build and deploy as 'release'"
	@echo "   deploy_test      Clean build and deploy as 'test'"
	@echo "   publish          Clean build and publish to PyPi"
	@echo ""

install:
	python setup.py install

clean:
	rm -rf ./autobahn.egg-info
	rm -rf ./build
	rm -rf ./dist
	find . -name "*.pyc" -type f -exec rm -f {} \;
	find . -name "*__pycache__" -type d -exec rm -rf {} \;

build: clean
	python setup.py bdist_egg

deploy_release: build
	sudo cp dist/*.egg /usr/local/www/tavendo_download/webmq/release/eggs/

deploy_test: build
	sudo cp dist/*.egg /usr/local/www/tavendo_download/webmq/test/eggs/

publish: clean
	python3 setup.py register
	python3 setup.py sdist upload
	#python setup.py bdist_egg upload
	#python setup.py bdist_wininst upload
