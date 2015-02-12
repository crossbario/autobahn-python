pyflakes:
	pyflakes .

pep8:
	pep8 --statistics --ignore=E501 -qq .
# pep8 --select=E231 --show-source

autopep8:
	autopep8 -ri --aggressive --ignore=E501 .

# This will run pep8, pyflakes and can skip lines that end with # noqa
flake8:
	flake8 -v --ignore=E501 autobahn

pylint:
	pylint -d line-too-long,invalid-name autobahn
