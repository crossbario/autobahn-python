# docs/conf.py
# autobahn-python documentation configuration - modernized for 2025
import os
import sys
from datetime import datetime

# -- Path setup --------------------------------------------------------------
# Add extensions directory and source directory to path
sys.path.insert(0, os.path.abspath("./_extensions"))
sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, os.path.abspath("."))

# monkey-patch txaio so that we can "use" both twisted *and* asyncio,
# at least at import time -- this is so the autodoc stuff can
# successfully import autobahn.twisted.* as well as autobahn.asyncio.*
# (usually, you can only import one or the other in a single Python
# interpreter)
import txaio


def use_tx():
    "monkey-patched for doc-building"
    from txaio import tx

    txaio._use_framework(tx)


def use_aio():
    "monkey-patched for doc-building"
    from txaio import aio

    txaio._use_framework(aio)


txaio.use_twisted = use_tx
txaio.use_asyncio = use_aio

# -- Project information -----------------------------------------------------
project = "autobahn"
author = "The WAMP/Autobahn/Crossbar.io OSS Project"
copyright = f"2011-{datetime.now():%Y}, typedef int GmbH (Germany)"

# Get version from the package
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
with open(os.path.join(base_dir, "src", "autobahn", "_version.py")) as f:
    exec(f.read())  # defines __version__

version = release = __version__

# -- General configuration ---------------------------------------------------
extensions = [
    # MyST Markdown support
    "myst_parser",

    # Core Sphinx extensions
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.ifconfig",
    "sphinx.ext.doctest",

    # Modern UX extensions
    "sphinx_design",
    "sphinx_copybutton",
    "sphinxext.opengraph",
    "sphinxcontrib.images",
    "sphinxcontrib.spelling",

    # API documentation
    "autoapi.extension",

    # Custom extension for Twisted/asyncio documentation
    "txsphinx",
]

# Source file suffixes (both RST and MyST Markdown)
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The master toctree document
master_doc = "index"

# Language
language = "en"

# Exclude patterns
exclude_patterns = ["_build", "work", "README.md", "DOCKER_BUILDS.md"]

# -- MyST Configuration ------------------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
    "attrs_block",
    "attrs_inline",
    "smartquotes",
    "linkify",
]
myst_heading_anchors = 3

# -- AutoAPI Configuration ---------------------------------------------------
autoapi_type = "python"
autoapi_dirs = ["../src/autobahn"]
autoapi_ignore = [
    "**/test/**",
    "test_*.py",
    "__main__.py",
    "*/__main__.py",
    "autobahn.__main__",
]
autoapi_add_toctree_entry = True
autoapi_root = "reference"
autoapi_options = [
    "members",
    "undoc-members",
    "private-members",
    "show-inheritance",
    "special-members",
    "show-module-summary",
]
autoapi_python_use_implicit_namespaces = True

# Suppress specific warnings
suppress_warnings = [
    "autoapi.python_import_resolution",
]

# -- Intersphinx Configuration -----------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "twisted": ("https://docs.twisted.org/en/stable/", None),
    "txaio": ("https://txaio.readthedocs.io/en/latest/", None),
}
intersphinx_cache_limit = 5

# -- HTML Output (Furo Theme) ------------------------------------------------
html_theme = "furo"
html_title = f"{project} {release}"

# Furo theme options with Noto fonts
html_theme_options = {
    # Source repository links
    "source_repository": "https://github.com/crossbario/autobahn-python/",
    "source_branch": "master",
    "source_directory": "docs/",

    # Noto fonts from Google Fonts
    "light_css_variables": {
        "font-stack": "'Noto Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "font-stack--monospace": "'Noto Sans Mono', SFMono-Regular, Menlo, Consolas, monospace",
    },
    "dark_css_variables": {
        "font-stack": "'Noto Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "font-stack--monospace": "'Noto Sans Mono', SFMono-Regular, Menlo, Consolas, monospace",
    },
}

# Logo (optimized SVG generated from docs/_graphics/ by `just _build-images`)
html_logo = "_static/img/autobahn_logo_blue.svg"

# Static files
html_static_path = ["_static"]
html_css_files = [
    # Load Noto fonts from Google Fonts
    "https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&family=Noto+Sans+Mono:wght@400;500&display=swap",
]

# -- sphinxcontrib-images Configuration --------------------------------------
images_config = {
    "override_image_directive": True,
    "default_image_width": "80%",
}

# -- Spelling Configuration --------------------------------------------------
spelling_lang = "en_US"
spelling_word_list_filename = "spelling_wordlist.txt"
spelling_show_suggestions = True

# -- OpenGraph (Social Media Meta Tags) -------------------------------------
ogp_site_url = "https://autobahn.readthedocs.io/en/latest/"

# -- Miscellaneous -----------------------------------------------------------
todo_include_todos = True
add_module_names = False
autosectionlabel_prefix_document = True
pygments_style = "sphinx"
autoclass_content = "both"

# RST Substitutions
rst_epilog = r"""
.. |ab| replace:: Autobahn
.. |Ab| replace:: **Autobahn**
.. |abL| replace:: Autobahn\|Python
.. |AbL| replace:: **Autobahn**\|Python
.. _Autobahn: http://crossbar.io/autobahn#python
.. _AutobahnJS: http://crossbar.io/autobahn#js
.. _AutobahnPython: **Autobahn**\|Python
.. _WebSocket: http://tools.ietf.org/html/rfc6455
.. _RFC6455: http://tools.ietf.org/html/rfc6455
.. _WAMP: http://wamp-proto.org/
.. _Twisted: http://twistedmatrix.com/
.. _asyncio: http://docs.python.org/3.4/library/asyncio.html
.. _CPython: http://python.org/
.. _PyPy: http://pypy.org/
.. _Jython: http://jython.org/
.. _AutobahnTestsuite: http://crossbar.io/autobahn#testsuite
.. _trollius: https://pypi.python.org/pypi/trollius/
.. _tulip: https://pypi.python.org/pypi/asyncio/
"""
