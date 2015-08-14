pyflakes:
	pyflakes .

pep8:
	pep8 --statistics --ignore=E501 -qq .
# pep8 --select=E231 --show-source

autopep8:
	autopep8 -ri --aggressive --ignore=E501 .

# This will run pep8, pyflakes and can skip lines that end with # noqa
flake8:
	flake8 --ignore=E501,E901,F401,F403,F811,F821,F841 .

pylint:
	pylint -d line-too-long,invalid-name .

examples:
	python run-all-examples.py
