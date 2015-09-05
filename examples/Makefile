pyflakes:
	pyflakes .

# run PEP8 check and print statistics
pep8:
	pep8 --statistics --ignore=E501 -qq .

# run PEP8 check and show source for offending code
pep8show:
	pep8 --show-source --ignore=E501 .

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
