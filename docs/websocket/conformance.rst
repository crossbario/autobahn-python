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

**With NVX Acceleration:**

* `Client Results (With NVX) <../_static/websocket/conformance/with-nvx/clients/index.html>`__ - Autobahn|Python WebSocket client conformance with NVX acceleration

**Without NVX Acceleration:**

* `Client Results (Without NVX) <../_static/websocket/conformance/without-nvx/clients/index.html>`__ - Autobahn|Python WebSocket client conformance without NVX acceleration

Server Conformance
~~~~~~~~~~~~~~~~~~~

**With NVX Acceleration:**

* `Server Results (With NVX) <../_static/websocket/conformance/with-nvx/servers/index.html>`__ - Autobahn|Python WebSocket server conformance with NVX acceleration

**Without NVX Acceleration:**

* `Server Results (Without NVX) <../_static/websocket/conformance/without-nvx/servers/index.html>`__ - Autobahn|Python WebSocket server conformance without NVX acceleration

Running Tests Locally
----------------------

You can run the conformance tests locally using the provided justfile recipes. Both **quick** and **full** test modes are supported.

Client Testing
~~~~~~~~~~~~~~

.. code-block:: bash

   # Terminal 1: Start the testsuite server (quick mode, default)
   just wstest-fuzzingserver
   # Or for full mode: just wstest-fuzzingserver "" "" full

   # Terminal 2: Test Twisted & asyncio clients across Python versions
   just wstest-testeeclient-twisted cpy311
   just wstest-testeeclient-twisted cpy314
   just wstest-testeeclient-twisted pypy311
   just wstest-testeeclient-asyncio cpy311
   just wstest-testeeclient-asyncio cpy314
   just wstest-testeeclient-asyncio pypy311

Test results will be generated in the ``.wstest/`` directory:

* ``.wstest/clients/`` - Client test results

Server Testing (6 combinations)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Terminal 1-6: Start all server combinations
   just wstest-testeeserver-twisted cpy311 "ws://127.0.0.1:9011"
   just wstest-testeeserver-asyncio cpy311 "ws://127.0.0.1:9012"
   just wstest-testeeserver-twisted cpy314 "ws://127.0.0.1:9013"
   just wstest-testeeserver-asyncio cpy314 "ws://127.0.0.1:9014"
   just wstest-testeeserver-twisted pypy311 "ws://127.0.0.1:9015"
   just wstest-testeeserver-asyncio pypy311 "ws://127.0.0.1:9016"

   # Terminal 7: Run testsuite client against all 6 servers
   just wstest-fuzzingclient
   # Or for full mode: just wstest-fuzzingclient "" "" full

Test results will be generated in the ``.wstest/`` directory:

* ``.wstest/servers/`` - Server test results

Consolidating Results for Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After running tests, consolidate the results for local documentation:

.. code-block:: bash

   # Copy test results to docs/_static and create JSON archive
   just wstest-consolidate-reports
   # Or for full mode results: just wstest-consolidate-reports full

This will:

* Copy HTML reports to ``docs/_static/websocket/conformance/``
* Create a ZIP archive with all JSON test files, one for clients and one for servers
* Make results available for local Sphinx documentation builds

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
