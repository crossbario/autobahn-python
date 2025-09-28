# Copyright (c) typedef int GmbH, Germany, 2025. All rights reserved.
#

# IMPORTANT:
# Ubuntu: sudo apt install gir1.2-girepository-2.0-dev
# Debian: https://pkgs.org/search/?q=girepository


# -----------------------------------------------------------------------------
# -- just global configuration
# -----------------------------------------------------------------------------

set unstable := true
set positional-arguments := true
set script-interpreter := ['uv', 'run', '--script']

# uv env vars
# see: https://docs.astral.sh/uv/reference/environment/

# project base directory = directory of this justfile
PROJECT_DIR := justfile_directory()

# Default recipe: list all recipes
default:
    @echo ""
    @just --list
    @echo ""

# Tell uv to always copy files instead of trying to hardlink them.
# set export UV_LINK_MODE := 'copy'

# Tell uv to use project-local cache directory.
export UV_CACHE_DIR := './.uv-cache'

# Use this common single directory for all uv venvs.
VENV_DIR := './.venvs'

# Define a justfile-local variable for our environments.
ENVS := 'cpy314 cpy313 cpy312 cpy311 pypy311'

# Internal helper to map Python version short name to full uv version
_get-spec short_name:
    #!/usr/bin/env bash
    set -e
    case {{short_name}} in
        cpy314)  echo "cpython-3.14";;  # cpython-3.14.0b3-linux-x86_64-gnu
        cpy313)  echo "cpython-3.13";;  # cpython-3.13.5-linux-x86_64-gnu
        cpy312)  echo "cpython-3.12";;  # cpython-3.12.11-linux-x86_64-gnu
        cpy311)  echo "cpython-3.11";;  # cpython-3.11.13-linux-x86_64-gnu
        pypy311) echo "pypy-3.11";;     # pypy-3.11.11-linux-x86_64-gnu
        *)       echo "Unknown environment: {{short_name}}" >&2; exit 1;;
    esac

# uv python install pypy-3.11-linux-aarch64-gnu --preview --verbose
# file /home/oberstet/.local/share/uv/python/pypy-3.11.11-linux-aarch64-gnu/bin/pypy3.11
# /home/oberstet/.local/share/uv/python/pypy-3.11.11-linux-aarch64-gnu/bin/pypy3.11: ELF 64-bit LSB executable, ARM aarch64, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux-aarch64.so.1, BuildID[sha1]=150f642a07dc36d3e465beaa0109e70da76ca67e, for GNU/Linux 3.7.0, stripped

# Internal helper that calculates and prints the system-matching venv name.
_get-system-venv-name:
    #!/usr/bin/env bash
    set -e
    SYSTEM_VERSION=$(/usr/bin/python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    ENV_NAME="cpy$(echo ${SYSTEM_VERSION} | tr -d '.')"

    if ! echo "{{ ENVS }}" | grep -q -w "${ENV_NAME}"; then
        echo "Error: System Python (${SYSTEM_VERSION}) maps to '${ENV_NAME}', which is not a supported environment in this project." >&2
        exit 1
    fi
    # The only output of this recipe is the name itself.
    echo "${ENV_NAME}"

# Helper recipe to get the python executable path for a venv
_get-venv-python venv="":
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        VENV_NAME=$(just --quiet _get-system-venv-name)
    fi
    VENV_PATH="{{VENV_DIR}}/${VENV_NAME}"

    # In your main recipes, replace direct calls to python with:
    # VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    # ${VENV_PYTHON} -V
    # ${VENV_PYTHON} -m pip -V

    if [[ "$OS" == "Windows_NT" ]]; then
        echo "${VENV_PATH}/Scripts/python.exe"
    else
        echo "${VENV_PATH}/bin/python3"
    fi

# -----------------------------------------------------------------------------
# -- General/global helper recipes
# -----------------------------------------------------------------------------

# Setup bash tab completion for the current user (to activate: `source ~/.config/bash_completion`).
setup-completion:
    #!/usr/bin/env bash
    set -e

    COMPLETION_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/bash_completion"
    MARKER="# --- Just completion ---"

    echo "==> Setting up bash tab completion for 'just'..."

    # Check if we have already configured it.
    if [ -f "${COMPLETION_FILE}" ] && grep -q "${MARKER}" "${COMPLETION_FILE}"; then
        echo "--> 'just' completion is already configured."
        exit 0
    fi

    echo "--> Configuration not found. Adding it now..."

    # 1. Ensure the directory exists.
    mkdir -p "$(dirname "${COMPLETION_FILE}")"

    # 2. Add our marker comment to the file.
    echo "" >> "${COMPLETION_FILE}"
    echo "${MARKER}" >> "${COMPLETION_FILE}"

    # 3. CRITICAL: Run `just` and append its raw output directly to the file.
    #    No `echo`, no `eval`, no quoting hell. Just run and redirect.
    just --completions bash >> "${COMPLETION_FILE}"

    echo "--> Successfully added completion logic to ${COMPLETION_FILE}."

    echo ""
    echo "==> Setup complete. Please restart your shell or run the following command:"
    echo "    source \"${COMPLETION_FILE}\""

# Remove ALL generated files, including venvs, caches, and build artifacts. WARNING: This is a destructive operation.
distclean:
    #!/usr/bin/env bash
    set -e

    echo "==> Performing a deep clean (distclean)..."

    # 1. Remove top-level directories known to us.
    #    This is fast for the common cases.
    echo "--> Removing venvs, cache, and build/dist directories..."
    rm -rf {{UV_CACHE_DIR}} {{VENV_DIR}} build/ dist/ wheelhouse/ .pytest_cache/ .ruff_cache/ .mypy_cache/

    # 2. Use `find` to hunt down and destroy nested artifacts that can be
    #    scattered throughout the source tree. This is the most thorough part.
    echo "--> Searching for and removing nested Python caches..."
    find . -type d -name "__pycache__" -exec rm -rf {} +

    echo "--> Searching for and removing compiled Python files..."
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete

    echo "--> Searching for and removing setuptools egg-info directories..."
    find . -type d -name "*.egg-info" -exec rm -rf {} +

    echo "--> Searching for and removing coverage data..."
    rm -f .coverage
    find . -type f -name ".coverage.*" -delete

    echo "==> Distclean complete. The project is now pristine."

# -----------------------------------------------------------------------------
# -- Python virtual environments
# -----------------------------------------------------------------------------

# List all Python virtual environments
list-all:
    #!/usr/bin/env bash
    set -e
    echo
    echo "Available CPython run-times:"
    echo "============================"
    echo
    uv python list --all-platforms cpython
    echo
    echo "Available PyPy run-times:"
    echo "========================="
    echo
    uv python list --all-platforms pypy
    echo
    echo "Mapped Python run-time shortname => full version:"
    echo "================================================="
    echo
    # This shell loop correctly uses a SHELL variable ($env), not a just variable.
    for env in {{ENVS}}; do
        # We call our helper recipe to get the spec for the current env.
        # The `--quiet` flag is important to only capture the `echo` output.
        spec=$(just --quiet _get-spec "$env")
        echo "  - $env => $spec"
    done
    echo
    echo "Create a Python venv using: just create <shortname>"

# Create a single Python virtual environment (usage: `just create cpy314` or `just create`)
create venv="":
    #!/usr/bin/env bash
    set -e

    VENV_NAME="{{ venv }}"

    # This is the "default parameter" logic.
    # If VENV_NAME is empty (because `just create` was run), calculate the default.
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi

    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")

    # Only create the venv if it doesn't already exist
    if [ ! -d "${VENV_PATH}" ]; then
        # Get the Python spec just-in-time
        PYTHON_SPEC=$(just --quiet _get-spec "${VENV_NAME}")

        echo "==> Creating Python virtual environment '${VENV_NAME}' using ${PYTHON_SPEC} in ${VENV_PATH}..."
        mkdir -p "{{ VENV_DIR }}"
        uv venv --seed --python "${PYTHON_SPEC}" "${VENV_PATH}"
        echo "==> Successfully created venv '${VENV_NAME}'."
    else
        echo "==> Python virtual environment '${VENV_NAME}' already exists in ${VENV_PATH}."
    fi

    ${VENV_PYTHON} -V
    ${VENV_PYTHON} -m pip -V

    echo "==> Activate Python virtual environment with: source ${VENV_PATH}/bin/activate"

# Meta-recipe to run `create` on all environments
create-all:
    #!/usr/bin/env bash
    for venv in {{ENVS}}; do
        just create ${venv}
    done

# Get the version of a single virtual environment's Python (usage: `just version cpy314`)
version venv="":
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"

    # This is the "default parameter" logic.
    # If VENV_NAME is empty (because `just create` was run), calculate the default.
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi

    if [ -d "{{ VENV_DIR }}/${VENV_NAME}" ]; then
        echo "==> Python virtual environment '${VENV_NAME}' exists:"
        "{{VENV_DIR}}/${VENV_NAME}/bin/python" -V
    else
        echo "==>  Python virtual environment '${VENV_NAME}' does not exist."
    fi
    echo ""

# Get versions of all Python virtual environments
version-all:
    #!/usr/bin/env bash
    for venv in {{ENVS}}; do
        just version ${venv}
    done

# Make Python packages installed by the OS package manager available in a managed venv. Usage: `just link-system-packages "" "/usr/lib/kicad-nightly/lib/python3/dist-packages"`
link-system-packages venv="" vendors="": (create venv)
    #!/usr/bin/env bash
    set -euo pipefail

    VENV_NAME="{{ venv }}"
    VENDOR_PATHS="{{ vendors }}"

    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi

    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"

    if [ ! -d "${VENV_PATH}" ] || [ ! -f "${VENV_PATH}/bin/python" ]; then
        echo "✗ Error: Virtual environment '${VENV_NAME}' not found at '${VENV_PATH}'." >&2
        exit 1
    fi
    echo "✓ Found virtual environment: ${VENV_PATH}"

    SYSTEM_PYTHON="/usr/bin/python3"
    SYSTEM_VERSION=$(${SYSTEM_PYTHON} -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

    # Collect all relevant site-packages directories (Debian + Ubuntu quirks)
    SYSTEM_SITE_PACKAGES=$(${SYSTEM_PYTHON} -c "import sysconfig, site, os, sys; paths={sysconfig.get_path('purelib')}; [paths.add(p) for p in site.getsitepackages() if os.path.isdir(p)]; print('\n'.join(sorted(paths)))")

    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    VENV_VERSION=$(${VENV_PYTHON} -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    VENV_SITE_PACKAGES=$(${VENV_PYTHON} -c "import sysconfig; print(sysconfig.get_path('purelib'))")

    echo "  - System Python ${SYSTEM_VERSION} site-packages: ${SYSTEM_SITE_PACKAGES}"
    echo "  - Venv   Python ${VENV_VERSION} site-packages: ${VENV_SITE_PACKAGES}"

    if [ "${VENV_VERSION}" != "${SYSTEM_VERSION}" ]; then
        echo "✗ Error: Python version mismatch!" >&2
        echo "  System is ${SYSTEM_VERSION}, but venv is ${VENV_VERSION}." >&2
        echo "  Cannot link system packages due to risk of binary incompatibility." >&2
        # exit 1
    fi
    echo "✓ Python versions match."

    PTH_FILE="${VENV_SITE_PACKAGES}/__system_packages.pth"
    echo "==> Writing link file: ${PTH_FILE}"

    {
        # system paths (multi-line safe)
        while IFS= read -r sp; do
            if [ -d "$sp" ]; then
                echo "$sp"
            else
                echo "⚠ Warning: system path not found: $sp" >&2
            fi
        done <<< "${SYSTEM_SITE_PACKAGES}"

        # vendor paths (comma/space separated)
        if [ -n "${VENDOR_PATHS}" ]; then
            IFS=', ' read -ra VENDOR_ARRAY <<< "${VENDOR_PATHS}"
            for vp in "${VENDOR_ARRAY[@]}"; do
                if [ -d "${vp}" ]; then
                    echo "${vp}"
                else
                    echo "⚠ Warning: vendor path not found: ${vp}" >&2
                fi
            done
        fi
    } > "${PTH_FILE}"

    echo "✓ Done."
    echo
    echo "Linked paths in $(basename "${PTH_FILE}"):"
    echo
    cat "${PTH_FILE}"
    echo

# -----------------------------------------------------------------------------
# -- Installation and Test
# -----------------------------------------------------------------------------

# Install this package and its run-time dependencies in a single environment (usage: `just install cpy314` or `just install`)
install venv="": (create venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Installing package with package runtime dependencies in ${VENV_NAME}..."
    # uv pip install --python "{{VENV_DIR}}/${VENV_NAME}/bin/python" .[all]
    ${VENV_PYTHON} -m pip install .[all]

# Install this package in development (editable) mode and its run-time dependencies in a single environment (usage: `just install-dev cpy314` or `just install-dev`)
install-dev venv="": (create venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Installing package - in editable mode - with package runtime dependencies in ${VENV_NAME}..."
    # uv pip install --python "{{VENV_DIR}}/${VENV_NAME}/bin/python" -e .[all]
    ${VENV_PYTHON} -m pip install -e .[all]

# Meta-recipe to run `install` on all environments
install-all:
    #!/usr/bin/env bash
    set -e
    for venv in {{ENVS}}; do
        just install ${venv}
    done

# Meta-recipe to run `install-dev` on all environments
install-dev-all:
    #!/usr/bin/env bash
    for venv in {{ENVS}}; do
        just install-dev ${venv}
    done

# -----------------------------------------------------------------------------
# -- Installation: Tools (Ruff, Sphinx, etc)
# -----------------------------------------------------------------------------

# Install the development tools for this Package in a single environment (usage: `just install-tools cpy314`)
install-tools venv="": (create venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Installing package development tools in ${VENV_NAME}..."

    ${VENV_PYTHON} -V
    ${VENV_PYTHON} -m pip -V

    # uv pip install --python "{{VENV_DIR}}/${VENV_NAME}/bin/python" -e .[dev]
    ${VENV_PYTHON} -m pip install -e .[dev]

# Meta-recipe to run `install-tools` on all environments
install-tools-all:
    #!/usr/bin/env bash
    set -e
    for venv in {{ENVS}}; do
        just install-tools ${venv}
    done

# Install Rust (rustc & cargo) from upstream via rustup.
install-rust:
    #!/usr/bin/env bash
    set -e
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    . "$HOME/.cargo/env"
    which rustc
    rustc --version
    which cargo
    cargo --version

# -----------------------------------------------------------------------------
# -- Linting, Static Typechecking, .. the codebase
# -----------------------------------------------------------------------------

# Automatically fix all formatting and code style issues.
autoformat venv="": (install-tools venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"

    echo "==> Automatically formatting code with ${VENV_NAME}..."

    # 1. Run the FORMATTER first. This will handle line lengths, quotes, etc.
    "${VENV_PATH}/bin/ruff" format --exclude ./tests ./autobahn

    # 2. Run the LINTER'S FIXER second. This will handle things like
    #    removing unused imports, sorting __all__, etc.
    "${VENV_PATH}/bin/ruff" check --fix --exclude ./tests ./autobahn
    echo "--> Formatting complete."

# Lint code using Ruff in a single environment
check-format venv="": (install-tools venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    echo "==> Linting code with ${VENV_NAME}..."
    "${VENV_PATH}/bin/ruff" check .

# Run static type checking with mypy
check-typing venv="": (install-tools venv) (install venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    echo "==> Running static type checks with ${VENV_NAME}..."
    "${VENV_PATH}/bin/mypy" autobahn/

# Run tests and generate an HTML coverage report in a specific directory.
check-coverage venv="": (install-tools venv) (install venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    echo "==> Running tests with coverage with ${VENV_NAME}..."
    mkdir -p docs/_build/html
    # for now, ignore any non-zero exit code by prefixing with hyphen (FIXME: remove later)
    "${VENV_PATH}/bin/pytest" \
        --cov=autobahn \
        --cov-report=html:docs/_build/html/coverage

    echo "--> Coverage report generated in docs/_build/html/coverage/index.html"

# Run all checks in single environment (usage: `just check cpy314`)
check venv="": (check-format venv) (check-typing venv) (check-coverage venv)

# -----------------------------------------------------------------------------
# -- Unit tests
# -----------------------------------------------------------------------------

# Run the test suite for Twisted/trial and asyncio/pytest (usage: `just test cpy314`)
test venv="": (test-twisted venv) (test-asyncio venv)

# Run the test suite for Twisted using trial (usage: `just test-twisted cpy314`)
test-twisted venv="": (install-tools venv) (install venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Running test suite for Twisted using trial in ${VENV_NAME}..."

    # IMPORTANT: Twisted trial doesn't allow to recurse-and-exclude, and hence we
    # need this looong explicit list of tests to run because we must exclude "asyncio"
    #
    # AUTOBAHN_CI_ENABLE_RNG_DEPLETION_TESTS=1:
    #   This enables "autobahn/test/test_rng.py" (on Linux), which tests entropy depletion,
    #   and tests how to correctly read _real_ entropy and block if not enough _real_ entropy
    #   is currently available (see: https://github.com/crossbario/autobahn-python/issues/1275)

    USE_TWISTED=1 ${VENV_PYTHON} -m twisted.trial --no-recurse \
        autobahn.test \
        autobahn.twisted.test \
        autobahn.websocket.test \
        autobahn.rawsocket.test \
        autobahn.wamp.test \
        autobahn.nvx.test

# Run the test suite for asyncio using pytest (usage: `just test-asyncio cpy314`)
test-asyncio venv="": (install-tools venv) (install venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Running test suite for asyncio using pytest in ${VENV_NAME}..."

    # IMPORTANT: we need to exclude all twisted tests
    USE_ASYNCIO=1 ${VENV_PYTHON} -m pytest -s -v -rfP \
        --ignore=./autobahn/twisted ./autobahn

# -----------------------------------------------------------------------------
# -- Documentation
# -----------------------------------------------------------------------------

# Build the HTML documentation using Sphinx
docs venv="": (install-tools venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    echo "==> Building documentation..."
    "${VENV_PATH}/bin/sphinx-build" -b html docs/ docs/_build/html

docs-view venv="": (docs venv)
    echo "==> Opening documentation in viewer ..."
    open docs/_build/html/index.html

# Clean the generated documentation
docs-clean:
    echo "==> Cleaning documentation build artifacts..."
    rm -rf docs/_build

# -----------------------------------------------------------------------------
# -- Building and Publishing
# -----------------------------------------------------------------------------

# Build distribution packages (wheels and source tarball)
build venv="": (install-tools venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Building distribution packages..."
    # Set environment variable for NVX acceleration
    AUTOBAHN_USE_NVX=1 ${VENV_PYTHON} -m build
    ls -la dist/

# Meta-recipe to run `build` on all environments
build-all:
    #!/usr/bin/env bash
    for venv in {{ENVS}}; do
        just build ${venv}
    done
    ls -la dist/

# Publish package to PyPI (requires twine setup)
publish venv="": (build venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    echo "==> Publishing to PyPI..."
    "${VENV_PATH}/bin/twine" upload dist/*

# -----------------------------------------------------------------------------
# -- FlatBuffers Schema Generation
# -----------------------------------------------------------------------------

# Clean generated FlatBuffers files
clean-fbs:
    echo "==> Cleaning FlatBuffers generated files..."
    rm -rf ./autobahn/wamp/gen/

# Build FlatBuffers schema files and Python bindings
build-fbs venv="":
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"

    FBSFILES="./autobahn/wamp/flatbuffers/*.fbs"
    FLATC="flatc"
    echo "==> Generating FlatBuffers binary schema and Python wrappers using $(${FLATC} --version)..."

    # Generate schema binary type library (*.bfbs files)
    ${FLATC} -o ./autobahn/wamp/gen/schema/ --binary --schema --bfbs-comments --bfbs-builtins ${FBSFILES}
    echo "--> Generated $(find ./autobahn/wamp/gen/schema/ -name '*.bfbs' | wc -l) .bfbs files"

    # Generate schema Python bindings (*.py files)
    ${FLATC} -o ./autobahn/wamp/gen/ --python ${FBSFILES}
    touch ./autobahn/wamp/gen/__init__.py
    echo "--> Generated $(find ./autobahn/wamp/gen/ -name '*.py' | wc -l) .py files"

    echo "Auto-formatting code using ruff after flatc code generation .."
    "${VENV_PATH}/bin/ruff" format ./autobahn/wamp/gen/
    "${VENV_PATH}/bin/ruff" check --fix ./autobahn/wamp/gen/

# -----------------------------------------------------------------------------
# -- File Management Utilities
# -----------------------------------------------------------------------------

# Rename audit files to replace ':' with '_' for Windows compatibility
fix-audit-filenames:
    #!/usr/bin/env bash
    set -e

    echo "==> Renaming audit files to replace ':' with '_' for Windows compatibility..."

    # Check if .audit directory exists
    if [ ! -d ".audit" ]; then
        echo "No .audit directory found, nothing to rename."
        exit 0
    fi

    # Count files that need renaming
    FILES_TO_RENAME=$(find .audit -name "*:*" -type f | wc -l)

    if [ "$FILES_TO_RENAME" -eq 0 ]; then
        echo "No files with ':' characters found in .audit directory."
        exit 0
    fi

    echo "Found $FILES_TO_RENAME files to rename:"
    find .audit -name "*:*" -type f
    echo ""

    # Rename files
    find .audit -name "*:*" -type f | while read -r file; do
        # Get directory and filename
        dir=$(dirname "$file")
        filename=$(basename "$file")

        # Replace : with _
        new_filename="${filename//:/_}"
        new_file="$dir/$new_filename"

        echo "Renaming: $filename -> $new_filename"
        mv "$file" "$new_file"
    done

    echo ""
    echo "==> Renaming complete! Updated files:"
    ls -la .audit/
    echo ""
    echo "These files are now Windows-compatible."
