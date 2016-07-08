Contribute
==========

|ab| is an open source project, and hosted on GitHub. The `GitHub repository <https://github.com/crossbario/autobahn-python>`_ includes the documentation.

We're looking for all kinds of contributions - from simple fixes of typos in the code or documentation to implementation of new features and additions of tutorials.

If you want to contribute to the code or the documentation:

Fork us on GitHub
-----------------

We use the Fork & Pull Model.

This means that you fork the repo, make changes to your fork, and then make a pull request here on the main repo.

This `article on GitHub <https://help.github.com/articles/using-pull-requests>`_ gives more detailed information on how the process works.


Running the Tests
-----------------

In order to run the unit-tests, we use `Tox <http://tox.readthedocs.org/en/latest/>`_ to build the various test-environments. To run them all, simply run ``tox`` from the top-level directory of the clone.

For test-coverage, see the Makefile target ``test_coverage``, which deletes the coverage data and then runs the test suite with various tox test-environments before outputting HTML annotated coverage to ``./htmlcov/index.html`` and a coverage report to the terminal.

There are two environment variables the tests use: ``USE_TWISTED=1`` or ``USE_ASYNCIO=1`` control whether to run unit-tests that are specific to one framework or the other.

See ``tox.ini`` for details on how to run in the different environments
