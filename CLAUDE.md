# Configuration and Policy for AI Assistants

Instructions **TO** _AI assistants_, e.g. Anthropic Claude,
Google Gemini, OpenAI ChatGPT, Microsoft Copilot, etc.

- Machine-readable guidelines that AI systems should follow
- not intended (primarily) for human contributors

> For notes and policies **FOR** _human contributors_ about using
> AI assistants, see [AI Policy](AI_POLICY.rst).

---

## Purpose

This document establishes guidelines for AI assistants e.g.
Anthropic Claude, Google Gemini, OpenAI ChatGPT, Microsoft
Copilot, etc. when working with this project's codebase. It aims
to ensure AI-generated contributions maintain our project's
quality standards and development practices.

## General Mantras

General mantras this project aims to follow:

- Do The Right Thing
- Secure by Design
- Secure by Default
- Make the Right Thing the Easy Thing
- Batteries included - It just works!
- No bullshit Bingo - No time to waste.

## Project Overview

The purpose of and an overview of this specific project can be
found in the top-level [Readme](README.rst).

## Group of Projects and WAMP

This project is member of a _group of projects_ all related to
[WAMP](https://wamp-proto.org/), and it is _crucial_ to
understand the interelation and dependencies between the projects
in the group. This is because those project "all fit together"
not by accident, but because they were _designed_ for this from
the very beginning. That's the whole reason they exist. WAMP.

It all starts fromq

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
_and_ **asyncio** (in the Python standard library).

The flexibility to allow users to switch the underlying
networking framework in **Autobahn|Python** between **Twisted**
and **asyncio** seamlessly, and with almost zero code changes on
the user side, is also crucial, and this capability is provided
by

- [txaio](https://github.com/crossbario/txaio/): txaio is a
  helper library for writing code that runs unmodified on both
  Twisted and asyncio / Trollius.

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

Finally, **Crossbar.io** has a number of advanced features
requiring persistence, for example _WAMP Event History_ (see
_WAMP Avanced Profile_) and others, and these capabilities build
on

- [zLMDB](https://github.com/crossbario/zlmdb): Object-relational
  in-memory database layer based on LMDB

which in turn is then used for the **Crossbar.io** specific
embedded database features

- [cfxdb](https://github.com/crossbario/cfxdb): cfxdb is a
  Crossbar.io Python support package with core database access
  classes written in native Python.

---

All Python projects within the _group of projects_, that is

- Autobahn|Python
- Crossbar.io
- txaio
- zLMDB
- cfxdb

must aim to

- Maintain compatibility across Python versions

when applicable

- Ensure consistent behavior between Twisted and asyncio backends

Further all Python projects must support both

- [CPython](https://www.python.org/), and
- [PyPy](https://pypy.org/)

as the Python (the language itself) run-time environment (the
language implementation).

This support is a MUST and a top-priority. Compatibility with
other Python run-time environments is currently not a priority.

Running on PyPy allows "almost C-like" performance, since PyPy is
a _tracing JIT compiler_ for Python with a _generational garbage
collector_. Both of these features are crucial for
high-performance, throughput/bandwidth and consistent low-latency
in networking or WAMP in particular.

For reasons too long to lay out here, it is of the essence to
only depend on Python-level dependencies in all of the Python
projects within the _group of projects_ which

- DO use [CFFI](https://cffi.readthedocs.io/en/latest/) to link
  native code, and
- NOT use CPyExt, the historically grown CPython extension API
  that is implementation defined only

This is a deep rabbit hole, but here is
[one link](https://pypy.org/posts/2018/09/inside-cpyext-why-emulating-cpython-c-8083064623681286567.html)
to dig into for some background.

---

## AI Assistant Guidelines

### 1. Code Contributions

The project requires careful attention to:

- **Maintain API compatibility**: Do not break existing public
  APIs
- **Follow existing patterns**: Study similar code in the project
  before proposing changes
- **Include type hints**: All new code should have proper type
  annotations
- **Write tests**: Every code change must include corresponding
  tests
- **Always check both backends** (when applicable): Any change
  must work correctly with both Twisted AND asyncio

### 2. Development Workflow

In generall, all development must follow the branch-per-feature
[GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)
branch strategy and development workflow.

Further, all development must follow

1. **Create an issue first**: All changes start with a GitHub
   issue describing the problem/feature
2. **Reference the issue**: PRs must reference the originating
   issue
3. **Pass all CI checks**: Code must pass all tests, linting, and
   coverage requirements
4. **Update documentation**: Changes affecting public APIs need
   documentation updates

Further, we aim for fully automated CI/CD (_not yet reality
everywhere unfortunately_) using
[GitHub Actions](https://docs.github.com/en/actions).

### 3. Code Style and Standards

- Use [Black](https://black.readthedocs.io/) for Python code formatting
- Use [Prettier](https://prettier.io/) for Markdown documentation formatting
- Use [rstfmt](https://github.com/dzhu/rstfmt) for ReST documentation formatting
- Use [Mypy](https://www.mypy-lang.org/) for additional type hinting (in addition to Python standard type hinting)
- Use [tox](https://tox.wiki/) for driving tests
- Use [Sphinx](https://www.sphinx-doc.org/) for Python documentation
- Use [Read the Docs](https://about.readthedocs.com/) to host documentation
- Follow PEP 8 with project-specific exceptions (see .flake8
  config)
- Use consistent import ordering (stdlib, third-party, local)
- Maintain existing code formatting patterns
- Preserve comment style and docstring format

### 4. Testing Requirements

- Write tests for both Twisted and asyncio backends
- Use the project's test utilities and fixtures
- Ensure tests are deterministic and don't rely on timing
- Cover edge cases, especially around error handling

### 5. Documentation

- Use reStructuredText format for all documentation
- Include docstrings for all public APIs
- Provide usage examples for new features
- Update CHANGELOG.md following existing format

## IP Policy Restrictions

### AI assistants MUST NOT:

1. **Generate substantial original algorithms** - Only assist
   with boilerplate, refactoring, or minor edits
2. **Create entire functions from scratch** - Limit assistance to
   modifying existing code patterns
3. **Produce novel architectural designs** - Refer users to
   maintainers for design decisions
4. **Generate more than 10 consecutive lines** of new logic
   without explicit human modification

### Acceptable AI Assistance:

- ✅ Fixing syntax errors
- ✅ Adapting existing patterns to new use cases
- ✅ Generating test boilerplate based on existing tests
- ✅ Refactoring for style compliance
- ✅ Writing docstrings for existing code

### Unacceptable AI Generation:

- ❌ Creating new algorithms or data structures
- ❌ Designing new API interfaces
- ❌ Implementing complete features from description alone
- ❌ Generating security-critical code

### Required Disclaimers:

When providing code assistance, AI must remind users:

```
"This AI-generated code requires human review and modification.
Contributors must comply with the project's AI_POLICY.rst regarding
disclosure and authorship warranties."
```

## What AI Should NOT Do

1. **Don't make breaking changes** without explicit discussion
2. **Don't add new dependencies** without maintainer approval
3. **Don't change CI/CD configuration** without understanding the
   full pipeline
4. **Don't modify licensing** or copyright headers
5. **Don't generate code that only works with one backend**
6. **Don't circumvent the IP Policy** restrictions defined above

## Getting Help

If an AI assistant is unsure about:

- Project conventions or patterns
- Compatibility requirements
- Testing approaches

It should recommend:

1. Reviewing similar existing code in the project
2. Checking the documentation at https://txaio.readthedocs.io
3. Asking for clarification in the GitHub issue
4. Consulting maintainer guidelines in CONTRIBUTING.md

---

_This document helps AI assistants provide better contributions
to this project. It is not a replacement for human review and
maintainer decisions._
