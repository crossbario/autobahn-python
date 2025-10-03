WebSocket Protocol Conformance
==============================

Autobahn|Python includes comprehensive WebSocket protocol conformance testing using the
`Autobahn|Testsuite <https://github.com/crossbario/autobahn-testsuite>`__, which provides
automated testing for RFC 6455 WebSocket protocol compliance.

Testing Overview
----------------

The conformance testing validates both WebSocket client and server implementations
across different Python async frameworks:

* **Client Testing**: Tests Autobahn|Python WebSocket clients against the Autobahn|Testsuite server (fuzzingserver mode)
* **Server Testing**: Tests Autobahn|Python WebSocket servers against the Autobahn|Testsuite client (fuzzingclient mode)

Both **Twisted** and **asyncio** backends are tested to ensure consistent behavior
across frameworks.

Test Results
------------

The latest conformance test results are generated automatically by our CI/CD pipeline:

Client Conformance
~~~~~~~~~~~~~~~~~~

* `Twisted Client Results <../_static/websocket/conformance/index.html>`__ - Autobahn|Python Twisted WebSocket client implementation
* `asyncio Client Results <../_static/websocket/conformance/index.html>`__ - Autobahn|Python asyncio WebSocket client implementation

Server Conformance
~~~~~~~~~~~~~~~~~~~

* `Server Results <../_static/websocket/conformance/index.html>`__ - Both Twisted and asyncio WebSocket server implementations tested together

Raw Test Data
~~~~~~~~~~~~~

Complete test results in JSON format are available for analysis and integration:

* `Download JSON Test Reports <../_static/websocket/conformance/conformance-reports-quick.zip>`__ - ZIP archive containing all JSON test result files

Running Tests Locally
----------------------

You can run the conformance tests locally using the provided justfile recipes:

Client Testing
~~~~~~~~~~~~~~

.. code-block:: bash

   # Terminal 1: Start the testsuite server
   just wstest-fuzzingserver

   # Terminal 2: Test Twisted client
   just wstest-testeeclient-twisted

   # Terminal 3: Test asyncio client  
   just wstest-testeeclient-asyncio

Server Testing
~~~~~~~~~~~~~~

.. code-block:: bash

   # Terminal 1: Start Twisted server
   just wstest-testeeserver-twisted

   # Terminal 2: Start asyncio server (different port)
   just wstest-testeeserver-asyncio

   # Terminal 3: Run testsuite client against both servers
   just wstest-fuzzingclient

Test results will be generated in the ``.wstest/`` directory:

* ``.wstest/clients/`` - Client test results
* ``.wstest/servers/`` - Server test results

Test Modes
----------

The testing infrastructure supports different test modes:

* **quick**: Fast subset of tests for development and CI
* **full**: Complete RFC 6455 test suite (extensive)

The CI pipeline runs in ``quick`` mode for faster feedback, while ``full`` mode
can be used for comprehensive validation.

About the Autobahn|Testsuite
-----------------------------

The `Autobahn|Testsuite <https://github.com/crossbario/autobahn-testsuite>`__ is the
industry-standard WebSocket protocol conformance testing suite. It provides:

* Comprehensive RFC 6455 protocol testing
* Fuzzing and edge case validation  
* Performance and robustness testing
* Detailed HTML and JSON reporting
* Cross-platform Docker-based execution

The testsuite is maintained by the same team that develops Autobahn|Python,
ensuring excellent integration and up-to-date testing capabilities.