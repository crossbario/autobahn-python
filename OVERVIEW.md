# WAMP Projects Overview

## The Group of Projects and WAMP

This project is member of a _group of projects_ all related to
[WAMP](https://wamp-proto.org/), and it is _crucial_ to
understand the interelation and dependencies between the projects
in the group.

This is because those project "all fit together" not by accident,
but because they were _designed_ for this from the very
beginning. That's the whole reason they exist. WAMP.

It all starts from

- [WAMP](https://github.com/wamp-proto/wamp-proto/): The Web
  Application Messaging Protocol (the protocol specification and
  website)

The WAMP protocol is the umbrella project, and compliance to its
specification is a _top-priority_ for the _WAMP Client Library
implementation projects_ in the _group of projects_:

- [Autobahn|Python](https://github.com/crossbario/autobahn-python/):
  WebSocket & WAMP for Python on Twisted and asyncio.
- [Autobahn|JS](https://github.com/crossbario/autobahn-js): WAMP
  for Browsers and NodeJS.
- [Autobahn|Java](https://github.com/crossbario/autobahn-java):
  WebSocket & WAMP in Java for Android and Java 8
- [Autobahn|C++](https://github.com/crossbario/autobahn-cpp):
  WAMP for C++ in Boost/Asio

The only _WAMP Router implementation project_ (currently) in the
_group of projects_ is

- [Crossbar.io](https://github.com/crossbario/crossbar):
  Crossbar.io is an open source networking platform for
  distributed and microservice applications. It implements the
  open Web Application Messaging Protocol (WAMP)

Again, compliance to the WAMP protocol implementation is a
_top-priority_ for Crossbar.io, as is compatibility with all
_WAMP Client Library implementation projects_ in the _group of
projects_.

Further, it is crucial to understand that **Crossbar.io** is a
Python project which builds on **Autobahn|Python**, and more so,
it builds on [Twisted](https://twisted.org/).

While **Crossbar.io** only runs on **Twisted**,
**Autobahn|Python** itself crucially supports _both_ **Twisted**
_and_ **asyncio** (in the Python standard library) - by design.

This flexibility to allow users of **Autobahn|Python** to switch
the underlying networking framework in **Autobahn|Python**
between **Twisted** and **asyncio** seamlessly, and with almost
zero code changes on the user side, is also crucial, and this
capability is provided by

- [txaio](https://github.com/crossbario/txaio/): txaio is a
  helper library for writing code that runs **unmodified** on
  **both** Twisted and asyncio / Trollius.

**Autobahn|Python** further provides both
[WebSocket](https://www.rfc-editor.org/rfc/rfc6455.html) _Client_
and _Server_ implementations, another crucial capability used in
Crossbar.io, the groups _WAMP Router implementation project_, and
in Autobahn|Python, the groups _WAMP Client Library
implementation project_ for Python application code.

Stemming from the participation of the original developer (Tobias
Oberstein) of the _group of projects_ in the IETF HyBi working
group during the RFC6455 specification, **Autobahn|Python** is
also the basis for

- [Autobahn|Testsuite](https://github.com/crossbario/autobahn-testsuite):
  The Autobahn|Testsuite provides a fully automated test suite to
  verify client and server implementations of The WebSocket
  Protocol (and WAMP) for specification conformance and
  implementation robustness.

**Autobahn|Python** fully conforms to RFC6455 and passes all of
the hundreds of WebSocket implementation tests in
**Autobahn|Testsuite**.

Finally, **Crossbar.io** has a number of advanced features
requiring **persistence**, for example _WAMP Event History_ (see
_WAMP Avanced Profile_) and others, and these capabilities build
on

- [zLMDB](https://github.com/crossbario/zlmdb): Object-relational
  transactional in-memory database layer based on LMDB

which in turn is then used for the **Crossbar.io** specific
embedded database features

- [cfxdb](https://github.com/crossbario/cfxdb): cfxdb is a
  Crossbar.io Python support package with core database access
  classes written in native Python.

## Important Files

Overview of Project Development Process, Release Process, User &
Developer Documentation, Contribution Policies, Audit Evidence,
and related Files.

### Files Unified across Projects

List of Files which are _Synchronized (copied) across
repositories:_

| File                                      | Format | Purpose                             | Where Rendered / Used |
| ----------------------------------------- | ------ | ----------------------------------- | --------------------- |
| OVERVIEW.md                               | MD     | Project Overview - _this_ file      | GitHub, Sphinx (MyST) |
| AI_POLICY.md                              | MD     | AI policy for contributors          | GitHub, Sphinx (MyST) |
| AI_AUDIT_PROCESS.md                       | MD     | Hard-evidence audit process         | GitHub, Sphinx (MyST) |
| AI_AUDIT_PROCESS_REVIEW.md                | MD     | Hard-evidence audit process review  | GitHub, Sphinx (MyST) |
| CLAUDE.md                                 | MD     | AI policy for AI assistants         | Used by AI assistants |
| .github/pull_request_template.md          | MD     | GitHub pull request template        | GitHub UI             |
| .github/ISSUE_TEMPLATE/config.yml         | MD     | GitHub issue template configuration | GitHub UI             |
| .github/ISSUE_TEMPLATE/bug_report.md      | MD     | GitHub bug issue template           | GitHub UI             |
| .github/ISSUE_TEMPLATE/feature_request.md | MD     | GitHub feature issue template       | GitHub UI             |
| sync_templates.py                         | Python | Synchronizes above files to repos   | Project Maintainer    |

### Files Specific to each Project

List of Files which are _Project- or Repository-specific (not
synchronized or copied):_

| File             | Format | Purpose                                  | Where Rendered / Used |
| ---------------- | ------ | ---------------------------------------- | --------------------- |
| README.md        | MD     | Project intro, quick links               | GitHub, Sphinx (MyST) |
| CONTRIBUTING.md  | MD     | Project development process, quick links | GitHub, Sphinx (MyST) |
| RELEASING.md     | MD     | Project release process, quick links     | GitHub, Sphinx (MyST) |
| docs/            | RST    | User/dev docs (with MD includes)         | Sphinx                |
| .audit/          | MD     | Audit evidence files (per PR) directory  | Git, GitHub UI        |
| .audit/README.md | MD     | Description of disclosure file contents  | Git, GitHub UI        |
