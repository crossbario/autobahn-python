all:
	@echo "Targets: run, install, clean"

run:
	PYTHONPATH="." python wampirc/service.py
	
install:
	python setup.py install

clean:
	find . -name "*.pyc" -exec rm -f {} \;
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
