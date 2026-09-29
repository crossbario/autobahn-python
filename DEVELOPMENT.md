# Development

Notes specific to **Autobahn|Python**: development setup, running the tests, supported runtimes,
and release versioning. The contribution workflow shared by all WAMP projects — GitHub issue first,
red → green tests, and the AI-assistance disclosure — is in [CONTRIBUTING.md](CONTRIBUTING.md).

## Getting in touch

Besides GitHub Issues and Discussions, there is the
[Autobahn mailing list](https://groups.google.com/forum/#!forum/autobahnws).

## Reporting bugs

In addition to what CONTRIBUTING.md asks for, please include:

- the Autobahn version: `python -c "import autobahn; print(autobahn.__version__)"`
- the networking framework in use: **Twisted** or **asyncio**
- relevant network configuration (proxy, firewall, TLS termination), if any

## Development setup

Development is driven by [`just`](https://github.com/casey/just) and [`uv`](https://github.com/astral-sh/uv);
run `just` to list all recipes. Every recipe takes the name of a managed virtual environment:
`cpy314`, `cpy313`, `cpy312`, `cpy311` (CPython) or `pypy311` (PyPy).

```bash
git clone https://github.com/crossbario/autobahn-python.git
cd autobahn-python
git submodule update --init --recursive
just create cpy314          # create the virtual environment
just install-dev cpy314     # editable install with run-time and development dependencies
```

## Running the tests

```bash
just test cpy314            # Twisted (trial) and asyncio (pytest)
just test-twisted cpy314
just test-asyncio cpy314
just test pypy311           # the same on PyPy
just check cpy314           # formatting, typing, coverage, serializers, compressors
```

The NVX native acceleration can be switched per run: `just test cpy314 1` (with) and
`just test cpy314 0` (without).

**Supported runtimes:** CPython 3.11–3.14 and PyPy 3.11, on both **Twisted and asyncio**. Changes
must work on both frameworks. Use [txaio](https://github.com/crossbario/txaio) for
framework-agnostic code, and don't break compatibility with either.

## Code style

`ruff` enforces formatting and linting (`just check-format cpy314`); the line length is 88. Add
docstrings for public APIs, and type hints for new code (`just check-typing cpy314`).

## Documentation

The documentation is reStructuredText, built with Sphinx: `just docs cpy314`.

## WebSocket conformance

WebSocket changes must keep passing [Autobahn|Testsuite](https://github.com/crossbario/autobahn-testsuite);
see `docs/websocket/conformance.rst` and the `wstest-*` recipes.

## Versioning

This project uses [CalVer](https://calver.org/) with PEP 440 development releases:
`YY.M.PATCH[.devN]` — for example, `26.7.1` for a stable release and `26.7.1.dev1` while in
development. Between releases the working tree always carries a `.devN` suffix.

The version is stored in two files kept in sync — `pyproject.toml` and `src/autobahn/_version.py` —
and managed with `just`:

- `just file-version` — show the current version (from both files)
- `just bump-dev` — bump to the next dev version for the current month (`YY.M.1.dev1`)
- `just bump-next 26.7.2.dev1` — set a specific next dev version
- `just prep-release` — strip the `.devN` suffix to cut a stable release

Git tags and releases are created by maintainers only.
