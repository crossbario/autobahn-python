# Contributing

We welcome contributions to **Autobahn|Python**! This guide explains how to
get involved.

## Getting in Touch

- **GitHub Issues**: Report bugs or request features at
  https://github.com/crossbario/autobahn-python/issues
- **GitHub Discussions**: Ask questions and discuss at
  https://github.com/crossbario/autobahn-python/discussions
- **Mailing List**: Join the Autobahn mailing list at
  https://groups.google.com/forum/#!forum/autobahnws
- **Chat**: Join us on the WAMP community channels

## Reporting Issues

When reporting issues, please include:

1. Python version (`python --version`)
2. Autobahn version (`python -c "import autobahn; print(autobahn.__version__)"`)
3. Operating system and version
4. Framework being used (Twisted or asyncio)
5. Minimal code example reproducing the issue
6. Full traceback if applicable
7. Network configuration if relevant (proxy, firewall, etc.)

## Contributing Code

1. **Fork the repository** on GitHub
2. **Create a feature branch** from `master`
3. **Make your changes** following the code style
4. **Add tests** for new functionality
5. **Run the test suite** to ensure nothing is broken
6. **Submit a pull request** referencing any related issues

## Development Setup

```bash
git clone https://github.com/crossbario/autobahn-python.git
cd autobahn-python
pip install -e .[dev,twisted,asyncio]
```

## Running Tests

```bash
# Run all tests
tox

# Run tests for specific Python version
tox -e py312

# Run specific test file
pytest autobahn/test/test_websocket.py
```

## Code Style

- Follow PEP 8
- Use meaningful variable and function names
- Add docstrings for public APIs
- Keep lines under 100 characters
- Use type hints where appropriate

## Documentation

- Documentation uses reStructuredText
- Build docs locally: `cd docs && make html`
- View at `docs/_build/html/index.html`

## Testing Both Frameworks

Autobahn|Python supports both Twisted and asyncio. When contributing:

- Test changes on both frameworks if applicable
- Use `txaio` for framework-agnostic code
- Don't break compatibility with either framework

## WebSocket Conformance

For WebSocket changes, run the Autobahn|Testsuite:

```bash
# See docs/websocket/conformance.rst for details
```

## License

By contributing to Autobahn|Python, you agree that your contributions will
be licensed under the MIT License.
